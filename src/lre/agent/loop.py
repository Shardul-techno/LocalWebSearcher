import hashlib
import json
import re
import threading
import time
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from lre.agent.parsing import parse_ids, parse_judgment, parse_queries
from lre.agent.prompts import PromptLibrary
from lre.core.events import Event
from lre.core.models import Answer, Passage, RankedPassage, Run, Selection, SourceDoc, TraceStep
from lre.passages.splitter import SplitConfig, split
from lre.passages.verify import page_hash


@dataclass
class ResearchContext:
    settings: dict
    project_root: Path
    llm: object
    search: object
    fetch: object
    ranker: object


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def research(context: ResearchContext, question: str, project: str = "inbox", mode: str = "search", style: str = "focused", cancel: threading.Event | None = None, on_event: Callable[[Event], None] | None = None) -> Run:
    cfg = context.settings
    cancel = cancel or threading.Event()
    emit = on_event or (lambda event: None)
    agent_cfg = cfg["agent"]
    mode_cfg = agent_cfg["modes"][mode]
    p_cfg = cfg["passages"]
    out_cfg = cfg["output"]
    prompt_lib = PromptLibrary(context.project_root / "prompts")
    trace: list[TraceStep] = []
    sources: list[SourceDoc] = []
    passages: list[Passage] = []
    candidates: list[Passage] = []
    selected: list[int] = []
    calls = 0
    temporary_pid = -1

    def ask(name: str, prompt: str) -> str | None:
        nonlocal calls
        if cancel.is_set() or calls >= agent_cfg["max_llm_calls_per_run"]:
            return None
        calls += 1
        started = time.monotonic()
        try:
            result = context.llm.generate(prompt)
            trace.append(TraceStep(name, _utc(), int((time.monotonic() - started) * 1000), {"call": calls}))
            return result
        except Exception as exc:
            trace.append(TraceStep(name, _utc(), int((time.monotonic() - started) * 1000), {"error": type(exc).__name__}))
            return None

    gap = ""
    pid_next = 1
    shown_ids: set[int] = set()
    for round_no in range(1, mode_cfg["rounds"] + 1):
        if cancel.is_set():
            break
        emit(Event("round", f"Research round {round_no}", round_no, mode_cfg["rounds"]))
        plan_prompt = prompt_lib.render("plan_queries", question=question, gap=gap, limit=mode_cfg["queries_per_round"])
        planned = ask("plan", plan_prompt)
        queries = parse_queries(planned or "", mode_cfg["queries_per_round"]) or ([question] if round_no == 1 else [])
        hits = []
        for query in queries:
            if cancel.is_set():
                break
            started = time.monotonic()
            try:
                hits.extend(context.search.search(query, cfg["search"]["results_per_query"]))
            except Exception as exc:
                trace.append(TraceStep("search", _utc(), int((time.monotonic() - started) * 1000), {"error": type(exc).__name__}))
        seen_urls = {source.url for source in sources}
        unique_hits = []
        for hit in hits:
            if hit.url not in seen_urls:
                seen_urls.add(hit.url)
                unique_hits.append(hit)
        top_hits = unique_hits[:mode_cfg["pages_per_round"]]
        for hit in top_hits:
            if cancel.is_set():
                break
            started = time.monotonic()
            try:
                page_text, digest = context.fetch.fetch(hit.url)
                doc_id = digest[:16]
                source = SourceDoc(doc_id, hit.url, hit.title, _utc(), digest)
                sources.append(source)
                slices = split(page_text, SplitConfig(p_cfg["target_chars"], p_cfg["max_chars"], p_cfg["min_chars"], p_cfg["overlap_sentences"]))
                new = [Passage(temporary_pid - i, doc_id, part.text, part.start, part.end, page_hash(page_text)) for i, part in enumerate(slices)]
                temporary_pid -= len(new)
                candidates.extend(new)
                trace.append(TraceStep("fetch_passages", _utc(), int((time.monotonic() - started) * 1000), {"url": hit.url, "passages": len(new)}))
            except Exception as exc:
                sources.append(SourceDoc(uuid.uuid4().hex[:16], hit.url, hit.title, _utc(), "", "error", type(exc).__name__))
                trace.append(TraceStep("fetch", _utc(), int((time.monotonic() - started) * 1000), {"url": hit.url, "error": type(exc).__name__}))
        style_top_k = cfg["agent"]["styles"][style]["top_k_to_model"]
        ranked = context.ranker.rank(question, passages + candidates, style_top_k)
        visible = [item for item in ranked if item.passage.pid not in shown_ids]
        # On later rounds, re-show the best passages already accumulated if there are no new ones.
        if not visible:
            visible = ranked
        visible = visible[:style_top_k]
        numbered: list[RankedPassage] = []
        for item in visible:
            passage = item.passage
            if passage.pid < 0:
                passage = replace(passage, pid=pid_next)
                pid_next += 1
                candidates = [candidate for candidate in candidates if candidate.pid != item.passage.pid]
                passages.append(passage)
                item = RankedPassage(passage, item.score)
            numbered.append(item)
        visible = numbered
        shown_ids.update(item.passage.pid for item in visible)
        if not visible:
            continue
        passage_text = "\n".join(f"[{item.passage.pid}] {item.passage.text[:p_cfg['max_chars_per_passage_in_prompt']]}" for item in visible)
        raw_selection = ask("select", prompt_lib.render("select_passages", question=question, passages=passage_text))
        valid_ids = [pid for pid in parse_ids(raw_selection or "") if pid in {item.passage.pid for item in visible}]
        if not valid_ids:
            valid_ids = [item.passage.pid for item in visible[:out_cfg["max_quotes"]]]
            selection_source = "fallback_bm25"
        else:
            selection_source = "llm"
        selected = list(dict.fromkeys(selected + valid_ids))[:out_cfg["max_quotes"]]
        chosen = [p for p in passages if p.pid in selected]
        judgment = ask("judge", prompt_lib.render("judge_sufficiency", question=question, passages="\n".join(f"[{p.pid}] {p.text[:p_cfg['max_chars_per_passage_in_prompt']]}" for p in chosen)))
        sufficient, gap = parse_judgment(judgment or "")
        trace.append(TraceStep("selection", _utc(), 0, {"source": selection_source, "pids": list(selected)}))
        if sufficient and agent_cfg["stop_on_sufficient"]:
            break

    if not selected:
        answer = Answer(None, "no_sources", ())
        selection = Selection((), "fallback_bm25")
    else:
        ranked = context.ranker.rank(question, [p for p in passages if p.pid in selected])
        ordered = tuple(item.passage.pid for item in ranked[:out_cfg["max_quotes"]])
        selection = Selection(ordered, "fallback_bm25" if any(step.info.get("source") == "fallback_bm25" for step in trace) else "llm")
        selected_passages = [p for p in passages if p.pid in ordered]
        summary_prompt = prompt_lib.render("summarize", question=question, passages="\n".join(f"[{p.pid}] {p.text[:p_cfg['max_chars_per_passage_in_prompt']]}" for p in selected_passages), max_sentences=out_cfg["max_summary_sentences"])
        summary_raw = ask("summarize", summary_prompt)
        valid_citations = set(ordered)
        citations = {int(value) for value in re.findall(r"\[(\d+)\]", summary_raw or "")}
        summary = re.sub(r"\[(\d+)\]", lambda match: match.group(0) if int(match.group(1)) in valid_citations else "", summary_raw or "").strip()
        if not summary or not citations.intersection(valid_citations):
            answer = Answer(None, "unavailable", ())
        else:
            answer = Answer(summary, "ok", tuple(sorted(citations.intersection(valid_citations))))

    digest = hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode("utf-8")).hexdigest()
    return Run(1, str(uuid.uuid4()), project, question, mode, cfg.get("llm", {}).get("active_model", "unknown"), _utc(), digest, tuple(sources), tuple(passages), selection, answer, tuple(trace))

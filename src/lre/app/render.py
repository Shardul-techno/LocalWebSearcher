from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from lre.core.models import Run
from lre.fetch.fetcher import cache_key
from lre.passages.textfragment import build
from lre.passages.verify import verify_passage


@dataclass(frozen=True)
class SourceLink:
    title: str
    domain: str
    url: str


@dataclass(frozen=True)
class Quote:
    pid: int
    text: str
    title: str
    url: str


@dataclass(frozen=True)
class RenderedRun:
    sources: tuple[SourceLink, ...]
    quotes: tuple[Quote, ...]
    summary: str
    plain_text: str


def render(run: Run, cache_dir: Path) -> RenderedRun:
    sources = {source.doc_id: source for source in run.sources}
    quotes: list[Quote] = []
    used: dict[str, SourceLink] = {}
    for pid in run.selection.pids:
        passage = next((item for item in run.passages if item.pid == pid), None)
        source = sources.get(passage.doc_id) if passage else None
        if not passage or not source:
            continue
        page = cache_dir / f"{cache_key(source.url)}.txt"
        if not page.exists():
            continue
        page_text = page.read_text(encoding="utf-8")
        if not verify_passage(passage, page_text):
            continue
        domain = urlsplit(source.url).netloc
        link = build(source.url, page_text[passage.start:passage.end])
        quotes.append(Quote(pid, page_text[passage.start:passage.end], source.title, link))
        used[source.doc_id] = SourceLink(source.title, domain, source.url)
    summary = run.answer.summary if quotes and run.answer.summary_status == "ok" else (
        "No supporting passages found" if run.answer.summary_status == "no_sources" else "Summary unavailable"
    )
    lines = ["SOURCES"]
    lines.extend(f"  {i}. {item.title} - {item.domain} - {item.url}" for i, item in enumerate(used.values(), 1))
    if not used:
        lines.append("  No verified sources")
    lines.extend(["", "QUOTES"])
    lines.extend(f'  [{quote.pid}] "{quote.text}"\n      {quote.title} - {quote.url}' for quote in quotes)
    if not quotes:
        lines.append("  No supporting passages found")
    lines.extend(["", "SUMMARY", f"  {summary}"])
    return RenderedRun(tuple(used.values()), tuple(quotes), summary, "\n".join(lines))

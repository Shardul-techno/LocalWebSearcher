"""Offline smoke test for source and packaged builds."""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from lre.app.render import render
from lre.core.models import Answer, Passage, Run, Selection, SourceDoc
from lre.fetch.extract import TrafilaturaExtractor
from lre.fetch.fetcher import cache_key
from lre.passages.ranker import BM25
from lre.passages.splitter import SplitConfig, split
from lre.passages.verify import page_hash
from lre.settings.loader import load_settings


def run(project_root: Path) -> tuple[bool, str]:
    try:
        load_settings(project_root / "config")
        html = (project_root / "tests" / "fixtures" / "article.html").read_text(encoding="utf-8")
        text = TrafilaturaExtractor().extract(html, "https://example.org/article")
        parts = split(text, SplitConfig(min_chars=20))
        if not parts:
            return False, "splitter returned no passages"
        passage = Passage(1, "doc", parts[0].text, parts[0].start, parts[0].end, page_hash(text))
        if not BM25().rank("energy storage", [passage]):
            return False, "BM25 returned no ranking"
        source = SourceDoc("doc", "https://example.org/article", "Fixture", datetime.now(timezone.utc).isoformat(), page_hash(text))
        run_data = Run(1, "selftest", "selftest", "energy storage", "simple", "fake", datetime.now(timezone.utc).isoformat(), "", (source,), (passage,), Selection((1,), "llm"), Answer("Fixture evidence [1].", "ok", (1,)), ())
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            (cache / f"{cache_key(source.url)}.txt").write_text(text, encoding="utf-8")
            result = render(run_data, cache)
        if len(result.quotes) != 1:
            return False, "rendering did not verify its fixture quote"
        return True, "config, extraction, passage verification, BM25 and rendering passed"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"

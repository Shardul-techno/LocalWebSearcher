import threading
from pathlib import Path

from lre.agent.loop import ResearchContext, research
from lre.core.models import SearchHit
from lre.llm.fake import FakeBackend
from lre.passages.ranker import BM25
from lre.passages.verify import verify_passage
from lre.search.fake import FakeSearchProvider
from lre.settings.loader import load_settings


class FakeFetcher:
    def fetch(self, url: str):
        text = "The device reduced energy use by 18 percent during the measured trial. This result was compared with the previous seasonal baseline."
        return text, "a" * 64


def test_fake_end_to_end_unknown_pids_fall_back_to_verified_passage():
    root = Path(__file__).parents[1]
    settings = load_settings(root / "config").values
    llm = FakeBackend(["energy device trial", "IDS: 999", "VERDICT: INSUFFICIENT | GAP: none", "The device reduced usage [1]."])
    ctx = ResearchContext(settings, root, llm, FakeSearchProvider([SearchHit("Trial", "https://example.org/trial")]), FakeFetcher(), BM25())
    run = research(ctx, "What changed in the trial?", mode="simple")
    assert run.selection.source == "fallback_bm25"
    assert run.selection.pids
    assert run.answer.summary_status == "ok"
    source = run.sources[0]
    passage = next(p for p in run.passages if p.pid == run.selection.pids[0])
    assert verify_passage(passage, FakeFetcher().fetch(source.url)[0])


def test_no_sources_never_generates_an_answer():
    root = Path(__file__).parents[1]
    settings = load_settings(root / "config").values
    ctx = ResearchContext(settings, root, FakeBackend(["query"]), FakeSearchProvider([]), FakeFetcher(), BM25())
    run = research(ctx, "unanswerable", mode="simple")
    assert run.answer.summary_status == "no_sources"
    assert run.answer.summary is None


def test_cancellation_after_search_stops_before_fetch():
    root = Path(__file__).parents[1]
    settings = load_settings(root / "config").values
    ctx = ResearchContext(settings, root, FakeBackend(["should not be used"]), FakeSearchProvider([SearchHit("x", "https://example.org")]), FakeFetcher(), BM25())
    cancel = threading.Event()
    class CancellingSearch(FakeSearchProvider):
        def search(self, query, limit):
            result = super().search(query, limit)
            cancel.set()
            return result
    ctx.search = CancellingSearch([SearchHit("x", "https://example.org")])
    run = research(ctx, "question", mode="simple", cancel=cancel)
    assert run.answer.summary_status == "no_sources"

from datetime import datetime, timezone
import shutil

import pytest

from lre.app.render import render
from lre.core.models import Answer, Passage, Run, Selection, SourceDoc, TraceStep
from lre.fetch.fetcher import cache_key
from lre.passages.verify import page_hash
from lre.storage.file_store import FileRunStore
from lre.llm.fake import FakeBackend
from lre.core.models import SearchHit
from lre.search.fake import FakeSearchProvider
from lre.fetch.fetcher import cache_key


def sample_run() -> tuple[Run, str]:
    url = "https://example.org/report"
    text = "Measured energy use fell by 18 percent in the trial."
    passage = Passage(1, "doc", text, 0, len(text), page_hash(text))
    source = SourceDoc("doc", url, "Trial report", datetime.now(timezone.utc).isoformat(), page_hash(text))
    run = Run(1, "12345678-1234-5678-1234-567812345678", "inbox", "What changed?", "simple", "qwen-small", datetime.now(timezone.utc).isoformat(), "settings", (source,), (passage,), Selection((1,), "llm"), Answer("Energy use fell [1].", "ok", (1,)), (TraceStep("search", datetime.now(timezone.utc).isoformat(), 1, {}),))
    return run, url


def test_file_store_round_trip_is_immutable_and_projects_are_folders(tmp_path):
    store = FileRunStore(tmp_path / "data")
    run, _ = sample_run()
    path = store.save(run)
    assert path.name.endswith("_12345678.json")
    assert store.load("inbox", run.run_id) == run
    assert store.list("inbox") == [run]
    assert store.create_project("research/subfolder").is_dir()
    original = path.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        store.save(run)
    assert path.read_text(encoding="utf-8") == original
    with pytest.raises(ValueError):
        store.create_project("../outside")


def test_render_only_emits_verified_verbatim_quotes(tmp_path):
    run, url = sample_run()
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / f"{cache_key(url)}.txt").write_text(run.passages[0].text, encoding="utf-8")
    rendered = render(run, cache)
    assert rendered.quotes[0].text == run.passages[0].text
    assert rendered.quotes[0].url.startswith(url + "#:~:text=")
    (cache / f"{cache_key(url)}.txt").write_text("tampered source text", encoding="utf-8")
    assert render(run, cache).quotes == ()


def test_service_ask_save_and_show_offline(tmp_path, monkeypatch):
    import lre.app.service as service_module

    root = tmp_path / "project"
    shutil.copytree("config", root / "config")
    shutil.copytree("prompts", root / "prompts")
    default = root / "config" / "default.toml"
    default.write_text(default.read_text(encoding="utf-8").replace('active_model = "managed-local"', 'active_model = "qwen-small"'), encoding="utf-8")
    search = FakeSearchProvider([SearchHit("Trial report", "https://example.org/trial")])
    monkeypatch.setattr(service_module, "DuckDuckGoProvider", lambda *args: search)
    monkeypatch.setattr(service_module, "build_backend", lambda profile: FakeBackend([
        "trial results", "IDS: 1", "VERDICT: SUFFICIENT", "Energy use declined [1]."
    ]))

    class CachedFetcher:
        def __init__(self, extractor, cache_dir, *args, **kwargs):
            self.cache_dir = cache_dir
        def fetch(self, url):
            text = "Energy use declined by 18 percent during the trial against a seasonal baseline measured the prior year."
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            (self.cache_dir / f"{cache_key(url)}.txt").write_text(text, encoding="utf-8")
            return text, cache_key(url)

    monkeypatch.setattr(service_module, "PageFetcher", CachedFetcher)
    service = service_module.ResearchService(root)
    run, output = service.ask("What happened in the trial?", mode="simple")
    loaded, reopened = service.show(run.run_id)
    assert loaded.run_id == run.run_id
    assert output.quotes == reopened.quotes
    assert "Energy use declined" in reopened.plain_text

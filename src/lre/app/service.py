from pathlib import Path
from typing import Callable

from lre.agent.loop import ResearchContext, research
from lre.core.events import Event
from lre.fetch.extract import TrafilaturaExtractor
from lre.fetch.fetcher import PageFetcher
from lre.llm.registry import build_backend
from lre.passages.ranker import BM25
from lre.search.ddg import DuckDuckGoProvider
from lre.search.wikipedia import WikipediaProvider
from lre.settings.loader import load_settings
from lre.storage.file_store import FileRunStore
from lre.app.render import RenderedRun, render
from lre.app.preferences import set_data_directory


class ResearchService:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.settings = load_settings(self.project_root / "config")
        app = self.settings.section("app")
        self.data_dir = Path(app["data_dir"])
        if not self.data_dir.is_absolute():
            self.data_dir = self.project_root / self.data_dir
        self.store = FileRunStore(self.data_dir)

    def ask(self, question: str, project: str | None = None, mode: str | None = None, style: str = "focused", model_profile: str | None = None, cancel=None, on_event: Callable[[Event], None] | None = None):
        values = dict(self.settings.values)
        values["llm"] = dict(values["llm"])
        if model_profile:
            values["llm"]["active_model"] = model_profile
        model_name = values["llm"]["active_model"]
        profile = self.settings.models[model_name]
        search_cfg = values["search"]
        if search_cfg["provider"] == "ddg":
            search = DuckDuckGoProvider(search_cfg["region"], search_cfg["safe_search"])
        elif search_cfg["provider"] == "wikipedia":
            search = WikipediaProvider(values["app"]["language"])
        else:
            raise ValueError(f"Unknown search provider: {search_cfg['provider']}")
        fetch_cfg = values["fetch"]
        fetch = PageFetcher(TrafilaturaExtractor(), self.data_dir / "cache", fetch_cfg["timeout_seconds"], fetch_cfg["max_bytes"], fetch_cfg["user_agent"], fetch_cfg["block_private_ips"], fetch_cfg["respect_robots_txt"])
        context = ResearchContext(values, self.project_root, build_backend(profile), search, fetch, BM25(values["passages"]["k1"], values["passages"]["b"], set(values["passages"]["stop_words"])))
        run = research(context, question, project or values["app"]["default_project"], mode or values["agent"]["default_mode"], style, cancel, on_event)
        self.store.save(run)
        return run, render(run, self.data_dir / "cache")

    def history(self, project: str | None = None):
        return self.store.list(project or self.settings.values["app"]["default_project"])

    def show(self, run_id: str, project: str | None = None) -> tuple[object, RenderedRun]:
        run = self.store.load(project or self.settings.values["app"]["default_project"], run_id)
        return run, render(run, self.data_dir / "cache")

    def projects(self) -> list[str]:
        return self.store.list_projects()

    def model_ready(self) -> tuple[bool, str]:
        from lre.app.doctor import check_model
        model_name = self.settings.values["llm"]["active_model"]
        return check_model(self.settings.models[model_name])

    def set_data_directory(self, data_dir: Path) -> None:
        set_data_directory(self.project_root / "config", data_dir)

    def doctor(self) -> list[tuple[str, bool, str]]:
        from lre.app.doctor import check_model
        model_name = self.settings.values["llm"]["active_model"]
        ok, message = check_model(self.settings.models[model_name])
        results = [("model", ok, message)]
        try:
            search_cfg = self.settings.values["search"]
            provider = DuckDuckGoProvider(search_cfg["region"], search_cfg["safe_search"]) if search_cfg["provider"] == "ddg" else WikipediaProvider()
            hits = provider.search("local research", 1)
            results.append(("search", bool(hits), "Search provider reachable" if hits else "Search returned no results"))
        except Exception as exc:
            results.append(("search", False, f"Search unavailable: {type(exc).__name__}"))
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            probe = self.data_dir / ".doctor-write-check"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            results.append(("storage", True, "Data directory writable"))
        except OSError as exc:
            results.append(("storage", False, f"Data directory unavailable: {type(exc).__name__}"))
        return results

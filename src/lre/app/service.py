from pathlib import Path
import os
import sys
from typing import Callable

from lre.agent.loop import ResearchContext, research
from lre.core.events import Event
from lre.fetch.extract import TrafilaturaExtractor
from lre.fetch.fetcher import PageFetcher
from lre.llm.registry import build_backend
from lre.llm.managed_server import ManagedServer
from lre.llm.model_manager import ModelManager
from lre.passages.ranker import BM25
from lre.search.ddg import DuckDuckGoProvider
from lre.search.wikipedia import WikipediaProvider
from lre.settings.loader import load_settings
from lre.settings.paths import resolve_paths
from lre.storage.file_store import FileRunStore
from lre.app.render import RenderedRun, render
from lre.app.preferences import migrate_legacy_layout, migrate_storage, set_active_model, set_storage_directory


class ResearchService:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
        self.paths = resolve_paths(self.project_root)
        self.settings = load_settings(self.project_root / "config", self.paths.user_config)
        app = self.settings.section("app")
        configured_root = app.get("storage_dir", "auto")
        self.storage_selection_required = configured_root == "auto"
        root = self.paths.storage_root if self.storage_selection_required else Path(configured_root).expanduser()
        if not root.is_absolute():
            root = self.project_root / root
        self._configure_storage(root)
        if self.storage_selection_required:
            if getattr(sys, "frozen", False):
                if self.paths.portable:
                    legacy_base = Path(sys.executable).parent
                    old_data, old_models, old_logs = legacy_base / "data", legacy_base / "models", legacy_base / "logs"
                else:
                    old_data = Path(os.environ.get("APPDATA", self.project_root / ".appdata")) / "LocalResearch" / "data"
                    old_models = Path(os.environ.get("LOCALAPPDATA", self.project_root / ".localappdata")) / "LocalResearch" / "models"
                    old_logs = Path(os.environ.get("APPDATA", self.project_root / ".appdata")) / "LocalResearch" / "logs"
            else:
                old_data = Path(app["data_dir"]) if app.get("data_dir", "auto") != "auto" else self.project_root / "data"
                old_models, old_logs = self.project_root / "models", self.project_root / "logs"
            migrate_legacy_layout(old_data, old_models, old_logs, self.storage_root)
        self.managed_server: ManagedServer | None = None

    def ask(self, question: str, project: str | None = None, mode: str | None = None, style: str = "focused", model_profile: str | None = None, cancel=None, on_event: Callable[[Event], None] | None = None):
        values = dict(self.settings.values)
        values["llm"] = dict(values["llm"])
        if model_profile:
            values["llm"]["active_model"] = model_profile
        model_name = values["llm"]["active_model"]
        profile = dict(self.settings.models[model_name])
        if profile["backend"] == "llamacpp_managed":
            model_path = self.model_manager.active_path()
            self.managed_server = self.managed_server or ManagedServer(self.project_root / "bin" / "llama-server.exe", model_path or Path(), self.log_dir, profile["num_ctx"], profile["threads"])
            profile["base_url"] = self.managed_server.start()
        search_cfg = values["search"]
        if search_cfg["provider"] == "ddg":
            search = DuckDuckGoProvider(search_cfg["region"], search_cfg["safe_search"])
        elif search_cfg["provider"] == "wikipedia":
            search = WikipediaProvider(values["app"]["language"], log_dir=self.log_dir)
        else:
            raise ValueError(f"Unknown search provider: {search_cfg['provider']}")
        fetch_cfg = values["fetch"]
        fetch = PageFetcher(TrafilaturaExtractor(), self.cache_dir, fetch_cfg["timeout_seconds"], fetch_cfg["max_bytes"], fetch_cfg["user_agent"], fetch_cfg["block_private_ips"], fetch_cfg["respect_robots_txt"], log_dir=self.log_dir)
        context = ResearchContext(values, self.project_root, build_backend(profile), search, fetch, BM25(values["passages"]["k1"], values["passages"]["b"], set(values["passages"]["stop_words"])))
        run = research(context, question, project or values["app"]["default_project"], mode or values["agent"]["default_mode"], style, cancel, on_event)
        self.store.save(run)
        return run, render(run, self.cache_dir)

    def history(self, project: str | None = None):
        return self.store.list(project or self.settings.values["app"]["default_project"])

    def show(self, run_id: str, project: str | None = None) -> tuple[object, RenderedRun]:
        run = self.store.load(project or self.settings.values["app"]["default_project"], run_id)
        return run, render(run, self.cache_dir)

    def projects(self) -> list[str]:
        return self.store.list_projects()

    def model_ready(self) -> tuple[bool, str]:
        from lre.app.doctor import check_model
        model_name = self.settings.values["llm"]["active_model"]
        profile = self.settings.models[model_name]
        if profile["backend"] == "llamacpp_managed":
            if not self.model_manager.active_path():
                return False, "No managed model is selected. Open Models… to install one."
            if not (self.project_root / "bin" / "llama-server.exe").is_file():
                return False, "llama-server.exe is missing. Run scripts\\fetch_llama_server.ps1 after its checksum is verified."
            return True, "Managed model is ready to start."
        return check_model(profile)

    def _configure_storage(self, storage_root: Path) -> None:
        self.storage_root = storage_root.expanduser().resolve()
        self.data_dir = self.storage_root / "data"
        self.cache_dir = self.storage_root / "cache"
        self.log_dir = self.storage_root / "logs"
        self.models_dir = self.storage_root / "models"
        self.temp_dir = self.storage_root / "temp"
        self.store = FileRunStore(self.data_dir)
        self.model_manager = ModelManager(self.models_dir, self.project_root / "config" / "model_catalog.toml")

    def set_storage_directory(self, storage_dir: Path) -> None:
        target = storage_dir.expanduser().resolve()
        migrate_storage(self.storage_root, target)
        set_storage_directory(self.paths.user_config, target)
        self._configure_storage(target)
        self.storage_selection_required = False

    def set_data_directory(self, data_dir: Path) -> None:
        self.set_storage_directory(data_dir)

    def models(self) -> list[dict]:
        return self.model_manager.list()

    def install_model(self, model_id: str, progress=None, cancel=None, confirm_hash=None) -> Path:
        return self.model_manager.install(model_id, progress, cancel, confirm_hash)

    def use_model(self, model_id: str, confirm_unverified: bool = False) -> Path:
        path = self.model_manager.set_active(model_id, confirm_unverified)
        set_active_model(self.paths.user_config, "managed-local")
        return path

    def remove_model(self, model_id: str) -> None:
        self.model_manager.remove(model_id)

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

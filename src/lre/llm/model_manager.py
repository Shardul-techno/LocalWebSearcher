"""User-initiated GGUF downloads and the small installed-model registry."""
import hashlib
import json
import shutil
import tomllib
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Event
from typing import Callable


class ModelError(RuntimeError):
    pass


@dataclass(frozen=True)
class CatalogModel:
    id: str
    name: str
    url: str
    sha256: str
    size_bytes: int
    context: int
    min_ram_mb: int
    license: str
    platforms: tuple[str, ...]
    recommended: bool


Progress = Callable[[int, int], None]
ConfirmHash = Callable[[str], bool]


class ModelManager:
    def __init__(self, models_dir: Path, catalog_file: Path):
        self.models_dir = models_dir
        self.catalog_file = catalog_file

    def catalog(self) -> list[CatalogModel]:
        with self.catalog_file.open("rb") as handle:
            raw = tomllib.load(handle)["models"]
        return [CatalogModel(**{**item, "platforms": tuple(item["platforms"])}) for item in raw]

    def list(self) -> list[dict]:
        installed = self._registry().get("models", {})
        return [{**asdict(model), "installed": installed.get(model.id)} for model in self.catalog()]

    def install(self, model_id: str, progress: Progress | None = None, cancel: Event | None = None, confirm_hash: ConfirmHash | None = None) -> Path:
        model = self._find(model_id)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(self.models_dir).free < model.size_bytes * 2:
            raise ModelError("Not enough free disk space for this model and its partial download")
        final = self.models_dir / f"{model.id}.gguf"
        partial = final.with_suffix(".gguf.part")
        digest = self._download(model.url, partial, model.size_bytes, progress, cancel)
        if model.sha256 and digest.lower() != model.sha256.lower():
            partial.unlink(missing_ok=True)
            raise ModelError("Downloaded model hash does not match the catalog")
        confirmed = bool(model.sha256)
        if not confirmed and confirm_hash:
            confirmed = confirm_hash(digest)
        partial.replace(final)
        registry = self._registry()
        registry.setdefault("models", {})[model.id] = {"path": final.name, "sha256": digest, "confirmed": confirmed}
        self._write_registry(registry)
        return final

    def remove(self, model_id: str) -> None:
        registry = self._registry()
        entry = registry.get("models", {}).pop(model_id, None)
        if not entry:
            raise ModelError("Model is not installed")
        (self.models_dir / entry["path"]).unlink(missing_ok=True)
        if registry.get("active") == model_id:
            registry.pop("active", None)
        self._write_registry(registry)

    def set_active(self, model_id: str, confirm_unverified: bool = False) -> Path:
        registry = self._registry()
        entry = registry.get("models", {}).get(model_id)
        if not entry:
            raise ModelError("Install the model before selecting it")
        if not entry["confirmed"] and not confirm_unverified:
            raise ModelError(f"Model hash is {entry['sha256']}; confirm it before use")
        entry["confirmed"] = True
        registry["active"] = model_id
        self._write_registry(registry)
        return self.models_dir / entry["path"]

    def active_path(self) -> Path | None:
        registry = self._registry()
        model_id = registry.get("active")
        entry = registry.get("models", {}).get(model_id)
        return self.models_dir / entry["path"] if entry else None

    def _find(self, model_id: str) -> CatalogModel:
        return next((model for model in self.catalog() if model.id == model_id), None) or self._unknown(model_id)

    def _unknown(self, model_id: str) -> CatalogModel:
        raise ModelError(f"Unknown catalog model: {model_id}")

    def _registry(self) -> dict:
        path = self.models_dir / "installed.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"models": {}}

    def _write_registry(self, value: dict) -> None:
        self.models_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.models_dir / ".installed.tmp"
        temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
        temporary.replace(self.models_dir / "installed.json")

    def _download(self, url: str, partial: Path, total: int, progress: Progress | None, cancel: Event | None) -> str:
        start = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(url, headers={"Range": f"bytes={start}-"} if start else {})
        with urllib.request.urlopen(request, timeout=30) as response:
            if start and response.status != 206:
                start = 0
                partial.unlink(missing_ok=True)
            downloaded = start
            hasher = hashlib.sha256()
            if start:
                with partial.open("rb") as existing:
                    for chunk in iter(lambda: existing.read(1024 * 1024), b""):
                        hasher.update(chunk)
            with partial.open("ab") as output:
                while True:
                    if cancel and cancel.is_set():
                        raise ModelError("Download cancelled; partial file kept for resume")
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    if progress:
                        progress(downloaded, total)
        return hasher.hexdigest()

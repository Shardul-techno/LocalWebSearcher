from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from lre.core.models import Answer, Passage, Run, Selection, SourceDoc, TraceStep


class FileRunStore:
    def __init__(self, data_dir: Path):
        self.projects_dir = data_dir / "projects"

    def _project_dir(self, project: str) -> Path:
        parts = project.replace("\\", "/").split("/")
        if not project or any(part in {"", ".", ".."} for part in parts) or ":" in project:
            raise ValueError("Invalid project path")
        path = self.projects_dir.joinpath(*parts).resolve()
        if not path.is_relative_to(self.projects_dir.resolve()):
            raise ValueError("Project path escapes data directory")
        return path

    def create_project(self, name: str) -> Path:
        path = self._project_dir(name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, run: Run) -> Path:
        folder = self.create_project(run.project)
        stamp = datetime.fromisoformat(run.created_at).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = folder / f"{stamp}_{run.run_id.replace('-', '')[:8]}.json"
        payload = json.dumps(asdict(run), ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(prefix=".run-", suffix=".tmp", dir=folder)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            Path(temp_name).rename(target)  # Fails rather than overwriting an existing immutable run.
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise
        return target

    def load(self, project: str, run_id: str) -> Run:
        folder = self._project_dir(project)
        candidates = list(folder.rglob("*.json"))
        for path in candidates:
            if run_id in {path.stem, path.stem.rsplit("_", 1)[-1]}:
                return _decode(json.loads(path.read_text(encoding="utf-8")))
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("run_id") == run_id:
                return _decode(raw)
        raise FileNotFoundError(f"Run not found: {run_id}")

    def list(self, project: str) -> list[Run]:
        folder = self._project_dir(project)
        if not folder.exists():
            return []
        runs = [_decode(json.loads(path.read_text(encoding="utf-8"))) for path in folder.rglob("*.json")]
        return sorted(runs, key=lambda run: run.created_at, reverse=True)

    def list_projects(self) -> list[str]:
        if not self.projects_dir.exists():
            return []
        return sorted(path.name for path in self.projects_dir.iterdir() if path.is_dir())


def _decode(raw: dict) -> Run:
    return Run(
        raw["schema_version"], raw["run_id"], raw["project"], raw["question"], raw["mode"], raw["model_profile"], raw["created_at"], raw["settings_digest"],
        tuple(SourceDoc(**item) for item in raw["sources"]),
        tuple(Passage(**item) for item in raw["passages"]),
        Selection(tuple(raw["selection"]["pids"]), raw["selection"]["source"]),
        Answer(raw["answer"]["summary"], raw["answer"]["summary_status"], tuple(raw["answer"]["cited_pids"])),
        tuple(TraceStep(**item) for item in raw["trace"]),
    )

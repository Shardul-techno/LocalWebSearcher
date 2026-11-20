"""Portable runtime locations; no UI or network imports."""
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    storage_root: Path
    data_dir: Path
    log_dir: Path
    models_dir: Path
    user_config: Path
    portable: bool


def resolve_paths(project_root: Path, environ: dict[str, str] | None = None,
                  frozen: bool | None = None, executable: Path | None = None) -> RuntimePaths:
    env = os.environ if environ is None else environ
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    exe = Path(sys.executable) if executable is None else executable
    appdata = Path(env.get("APPDATA", project_root / ".appdata"))
    if not is_frozen:
        root = project_root / "local_storage"
        return RuntimePaths(root, root / "data", root / "logs", root / "models",
                            project_root / "config" / "user.toml", False)
    if (exe.parent / "portable.flag").is_file():
        root = exe.parent / "LocalResearchData"
        return RuntimePaths(root, root / "data", root / "logs", root / "models",
                            exe.parent / "user.toml", True)
    root = appdata / "LocalResearch"
    return RuntimePaths(root, root / "data", root / "logs", root / "models",
                        root / "user.toml", False)

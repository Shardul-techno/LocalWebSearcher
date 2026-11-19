"""Portable runtime locations; this module deliberately has no UI or network imports."""
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    data_dir: Path
    log_dir: Path
    models_dir: Path
    user_config: Path
    portable: bool


def resolve_paths(project_root: Path, environ: dict[str, str] | None = None, frozen: bool | None = None, executable: Path | None = None) -> RuntimePaths:
    env = os.environ if environ is None else environ
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    exe = Path(sys.executable) if executable is None else executable
    appdata = Path(env.get("APPDATA", project_root / ".appdata"))
    localappdata = Path(env.get("LOCALAPPDATA", project_root / ".localappdata"))
    if not is_frozen:
        return RuntimePaths(project_root / "data", project_root / "logs", project_root / "models", project_root / "config" / "user.toml", False)
    root = exe.parent
    if (root / "portable.flag").is_file():
        return RuntimePaths(root / "data", root / "logs", root / "models", root / "user.toml", True)
    return RuntimePaths(appdata / "LocalResearch" / "data", appdata / "LocalResearch" / "logs", localappdata / "LocalResearch" / "models", appdata / "LocalResearch" / "user.toml", False)

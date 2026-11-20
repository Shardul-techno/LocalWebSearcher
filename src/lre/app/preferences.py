import hashlib
import json
import shutil
from pathlib import Path


_STORAGE_DIRS = ("data", "cache", "models", "logs", "temp", "assets")


def set_storage_directory(user_file: Path, storage_dir: Path) -> None:
    user_file.parent.mkdir(parents=True, exist_ok=True)
    value = f"storage_dir = {json.dumps(str(storage_dir.expanduser().resolve()))}"
    lines = user_file.read_text(encoding="utf-8").splitlines() if user_file.exists() else []
    output, in_app, updated = [], False, False
    for line in lines:
        if line.strip().startswith("["):
            if in_app and not updated:
                output.append(value)
                updated = True
            in_app = line.strip() == "[app]"
        if in_app and line.strip().startswith("storage_dir"):
            if not updated:
                output.append(value)
                updated = True
            continue
        output.append(line)
    if not updated:
        if not any(line.strip() == "[app]" for line in lines):
            output.extend(["", "[app]"])
        output.append(value)
    user_file.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _signature(root: Path) -> tuple[int, int]:
    files = [p for p in root.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def migrate_storage(source_root: Path, target_root: Path) -> None:
    """Copy and verify known storage folders. Never delete the source."""
    source_root, target_root = source_root.expanduser().resolve(), target_root.expanduser().resolve()
    if source_root == target_root:
        return
    target_root.mkdir(parents=True, exist_ok=True)

    def safe_copy(src_name: str, dst_name: str) -> str:
        src, dst = Path(src_name), Path(dst_name)
        if dst.exists():
            if not dst.is_file() or src.stat().st_size != dst.stat().st_size or _digest(src) != _digest(dst):
                raise FileExistsError(f"Refusing to overwrite different data: {dst}")
            return str(dst)
        shutil.copy2(src, dst)
        return str(dst)

    for name in _STORAGE_DIRS:
        src, dst = source_root / name, target_root / name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=safe_copy)
    for name in _STORAGE_DIRS:
        src, dst = source_root / name, target_root / name
        if src.is_dir() and _signature(src) != _signature(dst):
            raise OSError(f"Storage migration verification failed for {name}")


def set_data_directory(user_file: Path, data_dir: Path) -> None:
    """Compatibility alias: this path is now the unified storage root."""
    set_storage_directory(user_file, data_dir)


def set_active_model(user_file: Path, profile: str) -> None:
    _set_top_level(user_file, "llm", "active_model", profile)


def _set_top_level(user_file: Path, section: str, key: str, value: str) -> None:
    user_file.parent.mkdir(parents=True, exist_ok=True)
    line_value = f"{key} = {json.dumps(value)}"
    lines = user_file.read_text(encoding="utf-8").splitlines() if user_file.exists() else []
    output, inside, updated = [], False, False
    for line in lines:
        if line.strip().startswith("["):
            if inside and not updated:
                output.append(line_value)
                updated = True
            inside = line.strip() == f"[{section}]"
        if inside and line.strip().startswith(key):
            if not updated:
                output.append(line_value)
                updated = True
            continue
        output.append(line)
    if not updated:
        if not any(line.strip() == f"[{section}]" for line in lines):
            output.extend(([""] if output else []) + [f"[{section}]"])
        output.append(line_value)
    user_file.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")

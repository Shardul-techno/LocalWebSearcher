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
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _signature(root: Path) -> tuple[int, int]:
    files = [p for p in root.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


def _safe_copy(src_name: str, dst_name: str) -> str:
    src, dst = Path(src_name), Path(dst_name)
    if dst.exists():
        if not dst.is_file() or src.stat().st_size != dst.stat().st_size or _digest(src) != _digest(dst):
            raise FileExistsError(f"Refusing to overwrite different data: {dst}")
        return str(dst)
    shutil.copy2(src, dst)
    return str(dst)


def migrate_storage(source_root: Path, target_root: Path) -> None:
    """Copy and verify known storage folders. Never delete the source."""
    source_root, target_root = source_root.expanduser().resolve(), target_root.expanduser().resolve()
    if source_root == target_root:
        return
    if target_root.is_relative_to(source_root) or source_root.is_relative_to(target_root):
        raise ValueError("Choose a storage folder that is not inside the current storage folder (or vice versa).")
    target_root.mkdir(parents=True, exist_ok=True)
    for name in _STORAGE_DIRS:
        src, dst = source_root / name, target_root / name
        if src.is_dir() and src.resolve() != dst.resolve():
            shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=_safe_copy)
    for name in _STORAGE_DIRS:
        src, dst = source_root / name, target_root / name
        if src.is_dir() and src.resolve() != dst.resolve() and _signature(src) != _signature(dst):
            raise OSError(f"Storage migration verification failed for {name}")


def migrate_legacy_layout(data_dir: Path, models_dir: Path, logs_dir: Path, target_root: Path) -> None:
    """Import the previous split data/models/logs layout without deleting originals."""
    data_dir, models_dir, logs_dir = data_dir.expanduser().resolve(), models_dir.expanduser().resolve(), logs_dir.expanduser().resolve()
    target_root = target_root.expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    # Older versions kept project files and cache together under data/.
    data_target = target_root / "data"
    cache_target = target_root / "cache"
    if data_dir.is_dir():
        data_target.mkdir(parents=True, exist_ok=True)
        old_cache = data_dir / "cache"
        if old_cache.is_dir() and old_cache.resolve() != cache_target.resolve():
            shutil.copytree(old_cache, cache_target, dirs_exist_ok=True, copy_function=_safe_copy)
        if data_dir.resolve() != data_target.resolve():
            for item in data_dir.iterdir():
                if item.name == "cache":
                    continue
                target = data_target / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True, copy_function=_safe_copy)
                elif item.is_file():
                    _safe_copy(str(item), str(target))

    for source, name in ((models_dir, "models"), (logs_dir, "logs")):
        destination = target_root / name
        if source.is_dir() and source.resolve() != destination.resolve():
            shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=_safe_copy)

    # Verify the resulting folder trees against the legacy sources where applicable.
    if data_dir.is_dir() and data_dir.resolve() != data_target.resolve():
        for item in data_dir.iterdir():
            if item.name == "cache":
                continue
            copied = data_target / item.name
            if item.is_file() and (not copied.is_file() or _digest(item) != _digest(copied)):
                raise OSError("Legacy data migration verification failed")
    for source, name in ((models_dir, "models"), (logs_dir, "logs")):
        destination = target_root / name
        if source.is_dir() and source.resolve() != destination.resolve() and _signature(source) != _signature(destination):
            raise OSError(f"Legacy {name} migration verification failed")


def set_data_directory(user_file: Path, data_dir: Path) -> None:
    """Compatibility alias: selected path is now the unified storage root."""
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

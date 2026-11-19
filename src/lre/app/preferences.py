import json
from pathlib import Path


def set_data_directory(user_file: Path, data_dir: Path) -> None:
    """Store the M6 data-directory preference without parsing user-owned TOML."""
    user_file.parent.mkdir(parents=True, exist_ok=True)
    value = f"data_dir = {json.dumps(str(data_dir))}"
    if not user_file.exists():
        user_file.write_text(f"[app]\n{value}\n", encoding="utf-8")
        return
    lines = user_file.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    in_app = False
    updated = False
    for line in lines:
        if line.strip().startswith("["):
            if in_app and not updated:
                output.append(value)
                updated = True
            in_app = line.strip() == "[app]"
        if in_app and line.strip().startswith("data_dir"):
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


def set_active_model(user_file: Path, profile: str) -> None:
    _set_top_level(user_file, "llm", "active_model", profile)


def _set_top_level(user_file: Path, section: str, key: str, value: str) -> None:
    user_file.parent.mkdir(parents=True, exist_ok=True)
    line_value = f"{key} = {json.dumps(value)}"
    lines = user_file.read_text(encoding="utf-8").splitlines() if user_file.exists() else []
    output: list[str] = []
    inside = False
    updated = False
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

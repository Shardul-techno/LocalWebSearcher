import json
from pathlib import Path


def set_data_directory(config_dir: Path, data_dir: Path) -> None:
    """Store the M6 data-directory preference without parsing user-owned TOML."""
    user_file = config_dir / "user.toml"
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

import tomllib
from pathlib import Path
from typing import Any

from lre.settings.schema import Settings, make_typed


def _merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(config_dir: Path, user_file: Path | None = None) -> Settings:
    with (config_dir / "default.toml").open("rb") as handle:
        values = tomllib.load(handle)
    user_file = user_file or config_dir / "user.toml"
    if user_file.exists():
        with user_file.open("rb") as handle:
            values = _merge(values, tomllib.load(handle))
    with (config_dir / "models.toml").open("rb") as handle:
        models = tomllib.load(handle)
    if values["llm"]["active_model"] not in models:
        raise ValueError(f"Unknown active model profile: {values['llm']['active_model']}")
    typed = make_typed(values)
    return Settings(values, models, typed)

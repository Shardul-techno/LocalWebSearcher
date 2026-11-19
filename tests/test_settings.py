from pathlib import Path

from lre.settings.loader import load_settings


def test_settings_load_and_user_override(tmp_path: Path):
    default = Path(__file__).parents[1] / "config" / "default.toml"
    values = default.read_text(encoding="utf-8").replace('active_model = "qwen-small"', 'active_model = "one"')
    (tmp_path / "default.toml").write_text(values, encoding="utf-8")
    (tmp_path / "models.toml").write_text('[one]\nmodel="test"\n', encoding="utf-8")
    (tmp_path / "user.toml").write_text('[app]\ndata_dir="mine"\n', encoding="utf-8")
    settings = load_settings(tmp_path)
    assert settings.active_model["model"] == "test"
    assert settings.section("app")["data_dir"] == "mine"
    assert settings.typed.llm.active_model == "one"

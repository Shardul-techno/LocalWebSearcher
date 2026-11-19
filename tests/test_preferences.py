from pathlib import Path
import tomllib

from lre.app.preferences import set_data_directory


def test_data_directory_creates_minimal_override(tmp_path: Path):
    user = tmp_path / "user.toml"
    set_data_directory(user, Path("D:/Research Data"))
    with user.open("rb") as handle:
        assert tomllib.load(handle)["app"]["data_dir"] == str(Path("D:/Research Data"))


def test_data_directory_preserves_another_override(tmp_path: Path):
    user = tmp_path / "user.toml"
    user.write_text('[llm]\nactive_model = "other"\n\n[app]\nlog_dir = "logs"\n', encoding="utf-8")
    set_data_directory(user, Path("D:/Data"))
    with user.open("rb") as handle:
        settings = tomllib.load(handle)
    assert settings["llm"]["active_model"] == "other"
    assert settings["app"] == {"log_dir": "logs", "data_dir": str(Path("D:/Data"))}

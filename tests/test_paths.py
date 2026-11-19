from pathlib import Path

from lre.settings.paths import resolve_paths


def test_development_paths_stay_in_project(tmp_path: Path):
    paths = resolve_paths(tmp_path, frozen=False)
    assert paths.data_dir == tmp_path / "data"
    assert paths.log_dir == tmp_path / "logs"
    assert paths.models_dir == tmp_path / "models"
    assert paths.user_config == tmp_path / "config" / "user.toml"


def test_frozen_paths_use_user_locations(tmp_path: Path):
    env = {"APPDATA": "D:/Roaming", "LOCALAPPDATA": "D:/Local"}
    paths = resolve_paths(tmp_path, env, frozen=True, executable=tmp_path / "app" / "LocalResearch.exe")
    assert paths.data_dir == Path("D:/Roaming/LocalResearch/data")
    assert paths.log_dir == Path("D:/Roaming/LocalResearch/logs")
    assert paths.models_dir == Path("D:/Local/LocalResearch/models")
    assert paths.user_config == Path("D:/Roaming/LocalResearch/user.toml")


def test_portable_flag_overrides_frozen_paths(tmp_path: Path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "portable.flag").touch()
    paths = resolve_paths(tmp_path, frozen=True, executable=app_dir / "LocalResearch.exe")
    assert paths.portable
    assert paths.data_dir == app_dir / "data"
    assert paths.log_dir == app_dir / "logs"
    assert paths.user_config == app_dir / "user.toml"

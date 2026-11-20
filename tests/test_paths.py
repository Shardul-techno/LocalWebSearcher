from pathlib import Path

from lre.settings.paths import resolve_paths


def test_development_paths_share_selected_storage_root(tmp_path: Path):
    paths = resolve_paths(tmp_path, frozen=False)
    assert paths.storage_root == tmp_path / "local_storage"
    assert paths.data_dir == paths.storage_root / "data"
    assert paths.log_dir == paths.storage_root / "logs"
    assert paths.models_dir == paths.storage_root / "models"
    assert paths.user_config == tmp_path / "config" / "user.toml"


def test_frozen_paths_use_one_user_storage_root(tmp_path: Path):
    env = {"APPDATA": "D:/Roaming", "LOCALAPPDATA": "D:/Local"}
    paths = resolve_paths(tmp_path, env, frozen=True, executable=tmp_path / "app" / "LocalResearch.exe")
    assert paths.storage_root == Path("D:/Roaming/LocalResearch")
    assert paths.data_dir == paths.storage_root / "data"
    assert paths.log_dir == paths.storage_root / "logs"
    assert paths.models_dir == paths.storage_root / "models"


def test_portable_flag_uses_portable_storage_root(tmp_path: Path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "portable.flag").touch()
    paths = resolve_paths(tmp_path, frozen=True, executable=app_dir / "LocalResearch.exe")
    assert paths.portable
    assert paths.storage_root == app_dir / "LocalResearchData"
    assert paths.user_config == app_dir / "user.toml"

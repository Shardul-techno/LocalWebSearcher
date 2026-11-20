from pathlib import Path
import tomllib

import pytest

from lre.app.preferences import migrate_storage, set_storage_directory


def test_storage_directory_creates_minimal_override(tmp_path: Path):
    user = tmp_path / "user.toml"
    selected = tmp_path / "Research Data"
    set_storage_directory(user, selected)
    with user.open("rb") as handle:
        assert tomllib.load(handle)["app"]["storage_dir"] == str(selected.resolve())


def test_storage_directory_preserves_other_overrides(tmp_path: Path):
    user = tmp_path / "user.toml"
    user.write_text('[llm]\\nactive_model = "other"\\n\\n[app]\\nlog_dir = "logs"\\n', encoding="utf-8")
    set_storage_directory(user, tmp_path / "Data")
    with user.open("rb") as handle:
        settings = tomllib.load(handle)
    assert settings["llm"]["active_model"] == "other"
    assert settings["app"]["log_dir"] == "logs"


def test_migration_copies_and_preserves_original(tmp_path: Path):
    source, target = tmp_path / "old", tmp_path / "new"
    (source / "models").mkdir(parents=True)
    (source / "models" / "model.gguf").write_bytes(b"model-data")
    migrate_storage(source, target)
    assert (target / "models" / "model.gguf").read_bytes() == b"model-data"
    assert (source / "models" / "model.gguf").exists()


def test_migration_refuses_different_existing_file(tmp_path: Path):
    source, target = tmp_path / "old", tmp_path / "new"
    (source / "data").mkdir(parents=True)
    (target / "data").mkdir(parents=True)
    (source / "data" / "run.json").write_text("source")
    (target / "data" / "run.json").write_text("different")
    with pytest.raises(FileExistsError):
        migrate_storage(source, target)

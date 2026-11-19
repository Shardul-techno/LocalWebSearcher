from pathlib import Path

from lre.app.selftest import run


def test_offline_selftest_passes():
    passed, message = run(Path(__file__).parents[1])
    assert passed, message

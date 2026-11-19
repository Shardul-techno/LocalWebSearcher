# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).parent
datas = [
    (str(root / "config"), "config"),
    (str(root / "prompts"), "prompts"),
    (str(root / "tests" / "fixtures"), "tests/fixtures"),
    (str(root / "bin"), "bin"),
    (str(root / "LICENSE"), "."),
    (str(root / "THIRD_PARTY_NOTICES.md"), "."),
]
datas += collect_data_files("trafilatura")
# jusText resolves these XML stop lists relative to its package directory.
import justext
datas.append((str(Path(justext.__file__).parent / "stoplists"), "justext/stoplists"))

a = Analysis(
    [str(root / "packaging" / "launcher.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=datas,
    # trafilatura imports this standard-library extension indirectly.
    hiddenimports=["unicodedata"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
cli = EXE(pyz, a.scripts, [], exclude_binaries=True, name="lre", console=True)
ui = EXE(pyz, a.scripts, [], exclude_binaries=True, name="LocalResearch", console=False)
coll = COLLECT(cli, ui, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name="LocalResearch")

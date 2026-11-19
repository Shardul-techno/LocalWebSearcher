"""Frozen executable entry point; its filename selects CLI or desktop UI."""

import sys
from pathlib import Path


def main() -> int:
    if Path(sys.executable).stem.lower() == "localresearch":
        from lre.ui.tk_app import main as ui_main

        ui_main()
        return 0
    from lre.ui.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
from pathlib import Path

from lre.settings.loader import load_settings


def main() -> int:
    parser = argparse.ArgumentParser(prog="lre")
    parser.add_argument("command", nargs="?", default="doctor", choices=["doctor"])
    parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    settings = load_settings(root / "config")
    profile = settings.active_model
    print(f"Configuration OK; model profile {settings.values['llm']['active_model']} ({profile['model']}).")
    print("Local model and search-provider checks will be added in their milestones.")
    return 0

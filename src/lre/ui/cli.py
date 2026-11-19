import argparse
from pathlib import Path

from lre.settings.loader import load_settings
from lre.app.doctor import check_model


def main() -> int:
    parser = argparse.ArgumentParser(prog="lre")
    parser.add_argument("command", nargs="?", default="doctor", choices=["doctor"])
    parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    settings = load_settings(root / "config")
    profile = settings.active_model
    print(f"Configuration OK; model profile {settings.values['llm']['active_model']} ({profile['model']}).")
    if profile.get("backend") == "ollama":
        ready, message = check_model(profile)
        print(message)
        if not ready:
            print("Search-provider check will be added in M3.")
    return 0

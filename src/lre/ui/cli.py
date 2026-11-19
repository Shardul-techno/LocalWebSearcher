import argparse
import sys
from pathlib import Path

from lre.app.service import ResearchService
from lre.app.selftest import run as run_selftest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lre")
    commands = parser.add_subparsers(dest="command")
    ask = commands.add_parser("ask", help="research a question")
    ask.add_argument("question")
    ask.add_argument("--mode", choices=["simple", "search", "deep"], default=None)
    ask.add_argument("--project", default=None)
    ask.add_argument("--style", choices=["focused", "broad"], default="focused")
    ask.add_argument("--model", default=None)
    history = commands.add_parser("history", help="list saved runs")
    history.add_argument("--project", default=None)
    show = commands.add_parser("show", help="show a saved run")
    show.add_argument("run_id")
    show.add_argument("--project", default=None)
    commands.add_parser("projects", help="list projects")
    commands.add_parser("doctor", help="check model, search and storage")
    commands.add_parser("selftest", help="run the offline packaged-build smoke test")
    models = commands.add_parser("models", help="manage local GGUF models")
    model_commands = models.add_subparsers(dest="model_command", required=True)
    model_commands.add_parser("list", help="show catalog and installed models")
    install = model_commands.add_parser("install", help="download a catalog model")
    install.add_argument("model_id")
    remove = model_commands.add_parser("remove", help="remove an installed model")
    remove.add_argument("model_id")
    use = model_commands.add_parser("use", help="select an installed model")
    use.add_argument("model_id")
    use.add_argument("--confirm-sha256", action="store_true", help="confirm an unverified downloaded hash")
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = _parser().parse_args(argv or ["doctor"])
    service = ResearchService()
    if args.command == "selftest":
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
        passed, message = run_selftest(root)
        print(f"[{'ok' if passed else 'failed'}] selftest: {message}")
        return 0 if passed else 1
    if args.command == "ask":
        run, rendered = service.ask(args.question, args.project, args.mode, args.style, args.model)
        print(rendered.plain_text)
        print(f"\nSaved run: {run.run_id}")
    elif args.command == "history":
        runs = service.history(args.project)
        for run in runs:
            print(f"{run.created_at}  {run.run_id}  {run.question}")
        if not runs:
            print("No saved runs")
    elif args.command == "show":
        _, rendered = service.show(args.run_id, args.project)
        print(rendered.plain_text)
    elif args.command == "projects":
        projects = service.projects()
        print("\n".join(projects) if projects else "No projects")
    elif args.command == "models":
        if args.model_command == "list":
            for model in service.models():
                state = "installed" if model["installed"] else "available"
                print(f"{model['id']}  {state}  {model['size_bytes']} bytes  {model['name']}")
        elif args.model_command == "install":
            def progress(done: int, total: int) -> None:
                print(f"\rDownloading {done}/{total} bytes", end="", flush=True)
            path = service.install_model(args.model_id, progress, confirm_hash=lambda digest: _confirm(digest))
            print(f"\nInstalled: {path}")
        elif args.model_command == "remove":
            service.remove_model(args.model_id)
            print("Removed")
        else:
            print(f"Selected: {service.use_model(args.model_id, args.confirm_sha256)}")
    else:
        for name, ok, message in service.doctor():
            status = "ok" if ok else "unavailable"
            print(f"[{status}] {name}: {message}")
    return 0


def _confirm(digest: str) -> bool:
    answer = input(f"Catalog has no verified SHA-256. Computed: {digest}\nTrust this hash? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}

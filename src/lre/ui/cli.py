import argparse
import sys

from lre.app.service import ResearchService


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
    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = _parser().parse_args(argv or ["doctor"])
    service = ResearchService()
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
    else:
        for name, ok, message in service.doctor():
            status = "ok" if ok else "unavailable"
            print(f"[{status}] {name}: {message}")
    return 0

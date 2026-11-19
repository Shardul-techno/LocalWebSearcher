# Local Research Engine

A lightweight local web research app built around verifiable source passages.

## Setup

Use Python 3.11 on Windows. Run `scripts/setup.ps1` in PowerShell to create `.venv` and install the app.

## Run

```powershell
scripts/run_cli.ps1 doctor
scripts/run_cli.ps1 ask "What does the evidence say?" --mode search --project inbox
scripts/run_cli.ps1 history --project inbox
scripts/run_cli.ps1 show <run-id> --project inbox
```

Install the configured Ollama model with `ollama pull qwen3.5:0.8b`. Search and page fetches need internet access; inference is local. The Tk window is a later milestone.

The core package is portable Python. UI, network and extraction code are isolated so Android replacements can be added later. Run `python -m pytest` for the offline suite; integration tests are opt-in.

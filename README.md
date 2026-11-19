# Local Research Engine

A lightweight local web research app built around verifiable source passages.

## Setup

Use Python 3.11 on Windows. Run `scripts/setup.ps1` in PowerShell to create `.venv` and install the app.

## Run

Run `scripts/run_cli.ps1 doctor` to inspect configuration. Research commands will arrive in later milestones. Ollama runs locally; web requests are limited to configured search and page retrieval.

The core package is portable Python. UI, network and extraction code are isolated so Android replacements can be added later.

# Local Research Engine

A lightweight local web research app built around verifiable source passages.

## Developer setup

Install Python 3.11, then run this once in PowerShell from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
```

## Run

```powershell
scripts\run_cli.ps1 selftest
scripts\run_ui.ps1
```

The Models window downloads a GGUF only after you choose Install. Search and page fetches need internet access; inference remains local. `scripts\build_windows.ps1` verifies and bundles the pinned `llama-server` release.

The core package is portable Python. UI, network and extraction code are isolated so Android replacements can be added later.

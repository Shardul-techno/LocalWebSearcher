# Status

## Done
- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.
- M2 Ollama/OpenAI-compatible adapters, fake backend and tolerant output parsing.
- M3 DDGS/Wikipedia search adapters, SSRF-aware bounded fetcher, extraction and cache.
- M4 bounded multi-round loop with cancellation, traces, validated IDs and BM25 fallback.
- M5 immutable JSON storage, verified rendering, service facade and CLI commands.
- M6 Tkinter desktop UI with worker-thread research, history and clickable quotes.
- M7 portable paths, reproducible setup, model catalog/manager, managed llama-server integration and offline selftest.
- M8 packaging and CI: PyInstaller one-folder build, per-user Inno installer (`PrivilegesRequired=lowest` → `%LOCALAPPDATA%\Programs\LocalResearch`), portable zip + checksums, `fresh-setup` job, Windows package job with silent install / installed `selftest` / uninstall, release workflow on `v*` tags.
- CI fix (`6a23952`): immutable run saves use `O_CREAT|O_EXCL` then `os.replace` (POSIX rename no longer overwrites). Confirmed green on [44681766935](https://github.com/Shardul-techno/LocalWebSearcher/actions/runs/44681766935) at `19aab22`.

## In progress
- Stage 1 checkpoint measurements and a clean-machine manual install.

## Next
- Owner: install the CI artifact on a clean Windows account/Sandbox using `docs/testing-clean-install.md`.
- Download a catalog model and time one `search`-mode question on the laptop.
- Stage 2 (Android A1 + README rewrite) only after the owner says to continue.

## Known issues
- This developer Python 3.11 install has no `tkinter` module, so the Tk window cannot be launched here. M6 is verified by code review, offline `ResearchService` ask/save/show tests, and the Windows CI Tk smoke test; Ubuntu skips that smoke test when no display is available.
- Live research still needs a downloaded local model plus working web search.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Installer is unsigned; SmartScreen will warn (documented in the clean-install checklist).

## Unverified
- SHA-256 values for the catalog GGUF files; the app computes and requires confirmation before use.
- Clean-machine install (Windows Sandbox / fresh user) not run yet.
- Cold-start time and live `search`-mode timing not measured on this laptop.
- Exact on-disk installed size not measured locally (CI artifact zip size is available from the Actions run).

## Decisions needing the owner
- Confirm Stage 1 is accepted before Stage 2 (Android) begins.
- LICENSE is MIT placeholder; owner must confirm.

## How to run
- `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1`
- `.\.venv\Scripts\python.exe -m pytest -q`
- `.\.venv\Scripts\python.exe -m lre doctor`
- `.\.venv\Scripts\python.exe -m lre selftest`
- Packaged UI/CLI: download the `LocalResearch-Windows` artifact from the latest green CI run.

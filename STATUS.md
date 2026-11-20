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
- CI fix (`6a23952`): immutable run saves use `O_CREAT|O_EXCL` then `os.replace`, so duplicate saves raise `FileExistsError` on Windows and POSIX. Ubuntu and Windows test jobs plus offline selftests passed; `windows-package` built and uploaded artifacts on run [44679442165](https://github.com/Shardul-techno/LocalWebSearcher/actions/runs/44679442165).

## In progress
- M8 packaging and CI: per-user Inno installer, `fresh-setup` job, and silent install/selftest/uninstall in CI.

## Next
- Confirm the enhanced M8 CI workflow is green.
- Manual clean-install checklist in `docs/testing-clean-install.md` on a machine without Python.
- Live research query with a downloaded model; record timing.

## Known issues
- This developer Python 3.11 install has no `tkinter` module, so the Tk window cannot be launched here. M6 is verified by code review plus offline `ResearchService` ask/save/show tests; a machine with Tcl/Tk-enabled Python (or the packaged `LocalResearch.exe`) is still needed for a live UI click-through.
- The UI cannot perform live research until a local model is configured and web access is available.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.
- Live model/search timing was not measurable here: no managed model is installed and network search fails in this environment (`DDGSException` from `lre doctor`).

## Unverified
- SHA-256 values for the catalog GGUF files; the app computes and requires confirmation before use.
- Clean-machine install (Windows Sandbox / fresh user) not run yet.
- Packaged UI launch on a Tcl/Tk-capable runtime not exercised on this laptop.

## Decisions needing the owner
- None.

## How to run
- `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1`
- `.\.venv\Scripts\python.exe -m pytest -q`
- `.\.venv\Scripts\python.exe -m lre doctor`
- `.\.venv\Scripts\python.exe -m lre selftest`

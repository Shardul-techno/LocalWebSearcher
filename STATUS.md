# Status

## Current position

- Windows milestones M6, M7 and M8 are implemented in the repository.
- The active plan is now `CODEX_NEXT_STEPS.md`. It records completed Windows work and leaves Android A1/M9, shared contract M10/A2/A3 and the explicitly gated Stage 4 work outstanding.
- `My_Idea.md` contains the required **Model working** section and remains the source of truth for final-product requirements.
- The next permitted implementation stage is Stage 2 (A1 + M9), but first complete the outstanding Stage 1 Checkpoint 1 verification. Do not start Stage 2 until the owner explicitly authorizes it.

## Done

- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.
- M2 Ollama/OpenAI-compatible adapters, fake backend and tolerant output parsing.
- M3 DDGS/Wikipedia search adapters, SSRF-aware bounded fetcher, extraction and cache.
- M4 bounded multi-round loop with cancellation, traces, validated IDs and BM25 fallback.
- M5 immutable JSON storage, verified rendering, service facade and CLI commands.
- M6 Tkinter desktop UI with worker-thread research, history, clickable quotes, Run/Cancel, progress and project/mode controls. Enter submits the prompt. Shift+Enter multiline submission is not implemented because the current prompt control is single-line.
- M7 portable/runtime paths, reproducible setup, model catalog/manager, managed llama-server integration and offline selftest.
- M7 storage follow-up: first-run storage-root selection, later storage-location menu, separated data/cache/models/logs/temp/assets folders, migration/verification and retention of original files. Legacy split data/models/logs layouts are imported during first selection.
- M8 packaging and CI: PyInstaller one-folder build, per-user Windows installer, portable zip + checksums, fresh-setup job, Windows package job with silent install / installed selftest / uninstall, and release workflow on `v*` tags.
- Shared HTTP network helper in `src/lre/fetch/network.py`: bounded retries for transient network errors and selected HTTP statuses, exponential backoff with jitter, Retry-After handling, and redacted JSONL diagnostics. Integrated with page fetching and Wikipedia search; URL validation and isolated search-provider errors are logged.
- Network tests in `tests/test_network.py`.
- Documentation: `CODEX_NEXT_STEPS.md` created/updated to remove completed Windows implementation tasks from active work, record them as done, and retain the remaining Android/shared-contract/Stage 4 instructions.

## In progress / remaining

### Stage 1 — Checkpoint 1 verification only

- Record installer size.
- Record installed size.
- Measure cold start time.
- Measure one `search`-mode question on the owner's laptop with the bundled model.
- Run the manual clean-machine checklist in `docs/testing-clean-install.md` on Windows Sandbox or a fresh Windows user account.
- Do not invent measurements or mark the checkpoint complete until these are measured.

### Remaining requirements from My_Idea.md

- Shift+Enter must insert a newline while Enter submits. The current Tk prompt uses a single-line Entry, so this is not yet satisfied.
- Broader network hardening remains: the current helper is not yet proven against the complete requested matrix (DNS failures, certificate errors, redirect loops, malformed/empty responses, offline operation, interrupted downloads, and all timeout/cancellation cases). Add tests and improve only where gaps are demonstrated.
- Output truncation/incomplete-code detection, finish-reason preservation, controlled continuation and structural code validation are not implemented yet. These requirements must be planned without assuming model parameter increases alone solve the problem.
- Android A1/M9 and the shared Python/Kotlin contract M10/A2/A3 remain outstanding.
- Stage 4 sentence-span selection and the closed-set tool-call protocol remain explicitly gated. Do not start until the owner says so.

## Known issues

- This developer Python 3.11 install has no `tkinter` module, so the Tk window cannot be launched in this environment. M6 is covered by UI tests and Windows CI smoke coverage; actual local GUI behaviour still needs the owner's machine.
- Live research needs a downloaded local model plus working web search.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Installer is unsigned; SmartScreen will warn (documented in the clean-install checklist).

## Unverified

- Clean-machine install (Windows Sandbox / fresh user) not run yet.
- Cold-start time and live `search`-mode timing not measured on the owner's laptop.
- Exact installed size has not been measured locally.
- GGUF catalog SHA-256 values are not all independently verified against official model releases; where the catalog hash is absent, the manager computes a hash and requires confirmation before use.
- Latest remote CI check (2026-11-20): workflow run [#37](https://github.com/Shardul-techno/LocalWebSearcher/actions/runs/44736964563) for commit `087c5a71` is **queued**; its Windows, Ubuntu and fresh-setup jobs have not started. The commit status is pending with no reported checks. No passing result is currently verified.
- `CODEX_INSTRUCTIONS.md`, which `CODEX_NEXT_STEPS.md` says contains the inherited M0–M5 rules, is not present in the repository. `AGENTS.md` exists, but it contains project context and a copy of the product requirements, not the missing inherited M0–M5 implementation rules. Restore the correct file or confirm its authoritative location before treating those inherited rules as available to a fresh contributor.

## Decisions needing the owner

- Confirm Stage 1 Checkpoint 1 measurements and clean-machine test.
- Explicitly authorize Stage 2 (Android A1 + README rewrite) after Checkpoint 1.
- LICENSE is MIT placeholder; owner must confirm.

## Verification attempt — 2026-11-20

- Attempted a fresh clone so the prescribed tests and `python -m lre doctor` / `python -m lre selftest` could be run. The execution environment could not resolve `github.com` (DNS failure), so no repository code was executed locally in this session.
- GitHub Actions run #37 is queued and has not provided test evidence yet. Do not treat the queued run as a pass.
- The repository tree currently has no `android/` directory and no `.github/workflows/android.yml`; this is expected because Stage 2 has not begun.
- `My_Idea.md` was read and not modified.

## How to run

- `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1`
- `.\.venv\Scripts\python.exe -m pytest -q`
- `.\.venv\Scripts\python.exe -m lre doctor`
- `.\.venv\Scripts\python.exe -m lre selftest`
- Packaged UI/CLI: download the `LocalResearch-Windows` artifact from the latest green CI run.

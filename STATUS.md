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

## In progress
- M8 packaging and CI (Windows packaging job was skipped while Ubuntu tests failed).

## Next
- Land the immutable-run save fix so Ubuntu CI and `windows-package` can run.
- Finish M8, then run a live research query and record model timing.

## Known issues
- Ubuntu CI failed on `test_file_store_round_trip_is_immutable_and_projects_are_folders`: POSIX `Path.rename` overwrote an existing run instead of raising `FileExistsError`. Fix: exclusive `O_CREAT|O_EXCL` claim before `os.replace`.
- The UI cannot perform live research until a local model is configured and web access is available.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.
- Live model/search timing was not measurable here: Ollama is unreachable and network search fails in this environment.

## Unverified
- SHA-256 values for the catalog GGUF files; the app computes and requires confirmation before use.

## Decisions needing the owner
- None.

## How to run
- `python -m pytest`
- `python -m lre doctor`

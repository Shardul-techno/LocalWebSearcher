# Status

## Done
- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.
- M2 Ollama/OpenAI-compatible adapters, fake backend and tolerant output parsing.
- M3 DDGS/Wikipedia search adapters, SSRF-aware bounded fetcher, extraction and cache.
- M4 bounded multi-round loop with cancellation, traces, validated IDs and BM25 fallback.
- M5 immutable JSON storage, verified rendering, service facade and CLI commands.
- M6 Tkinter desktop UI with worker-thread research, history and clickable quotes.

## In progress
- Stage 1 installability work: portable paths, model manager and packaged runtime.

## Next
- Finish M7 and M8, then run a live research query and record model timing.

## Known issues
- The UI cannot perform live research until a local model is configured and web access is available.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.
- Live model/search timing was not measurable here: Ollama is unreachable and network search fails in this environment.

## Decisions needing the owner
- None.

## How to run
- `python -m pytest`
- `python -m lre doctor`

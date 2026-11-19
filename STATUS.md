# Status

## Done
- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.
- M2 Ollama/OpenAI-compatible adapters, fake backend and tolerant output parsing.
- M3 DDGS/Wikipedia search adapters, SSRF-aware bounded fetcher, extraction and cache.
- M4 bounded multi-round loop with cancellation, traces, validated IDs and BM25 fallback.
- M5 immutable JSON storage, verified rendering, service facade and CLI commands.

## In progress
- Live end-to-end run against installed Ollama plus reachable search requires the owner’s machine/network.

## Next
- M6 minimal Tkinter UI, then run a live research query and record model timing.

## Known issues
- Tk UI is not implemented yet; it is the M6 step.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.
- Live model/search timing was not measurable here: Ollama is unreachable and network search fails in this environment.

## Decisions needing the owner
- None.

## How to run
- `python -m pytest`
- `python -m lre doctor`

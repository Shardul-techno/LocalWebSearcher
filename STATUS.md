# Status

## Done
- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.
- M2 Ollama/OpenAI-compatible adapters, fake backend and tolerant output parsing.
- M3 DDGS/Wikipedia search adapters, SSRF-aware bounded fetcher, extraction and cache.

## In progress
- M4 bounded agent loop and offline end-to-end tests.

## Next
- Continue M4, then immutable storage, app facade and CLI through M5.

## Known issues
- Search/fetch, agent loop, persistence, CLI research and Tk UI are not implemented yet.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.

## Decisions needing the owner
- None.

## How to run
- `python -m pytest`
- `python -m lre doctor`

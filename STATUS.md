# Status

## Done
- M0 scaffold and typed TOML loader.
- M1 exact passage slices, BM25, hash verification and text-fragment links.

## In progress
- M2 local LLM adapters and tolerant parsing.

## Next
- Continue M2, then search/fetch, bounded agent loop and CLI through M5.

## Known issues
- Search/fetch, agent loop, persistence, CLI research and Tk UI are not implemented yet.
- The 0.8B model may struggle with query planning and summaries; BM25 fallback remains essential.
- Android is a future target; this phase only keeps core logic portable.

## Decisions needing the owner
- None.

## How to run
- `python -m pytest`
- `python -m lre doctor`

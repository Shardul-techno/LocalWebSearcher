# Architecture

This document describes the current implementation. The product requirements remain in `My_Idea.md`; the implementation sequence is in `CODEX_NEXT_STEPS.md`.

## Current architecture

The application is a portable Python core with replaceable adapters and two front ends: a Tkinter desktop UI and a CLI. The app service is the composition root. Platform-specific code should remain outside the portable core.

```text
Tk UI / CLI
    |
    v
ResearchService  ------------------ user preferences / storage selection
    |
    +--> Settings loader
    |
    +--> Agent loop
    |      |
    |      +--> SearchProvider
    |      +--> PageFetcher -> URL safety -> HTTP retry/diagnostics -> Extractor
    |      +--> Ranker (BM25)
    |      +--> LlmBackend
    |
    +--> FileRunStore
    |
    +--> Verified renderer -> Sources / Quotes / Summary
```

## Module responsibilities

| Module | Responsibility | Replaceable boundary |
|---|---|---|
| `core/` | Portable data models and events | Shared models/interfaces |
| `settings/` | TOML loading, typed validation and runtime paths | Configuration source and path policy |
| `search/` | Search-provider implementations | `SearchProvider` |
| `fetch/` | URL validation, bounded HTTP requests, diagnostics, extraction and cache | Fetcher and extractor |
| `passages/` | Text splitting, BM25 ranking, exact-slice verification and text-fragment links | `Ranker` and passage functions |
| `llm/` | Local inference adapters, managed llama.cpp lifecycle and model downloads | `LlmBackend` |
| `agent/` | Bounded planning, search, selection, sufficiency judgement and summary | Interfaces in `ResearchContext` |
| `storage/` | Immutable JSON run files | `RunStore` |
| `app/` | Composition, user preferences, migration and rendering | `ResearchService` facade |
| `ui/` | Tkinter desktop UI and CLI | Calls the app facade only |

## Dependency rule

1. `core` must not import UI, network, database or model-runtime packages.
2. Adapters depend on portable interfaces and settings; they must not make the core depend on a specific provider.
3. The agent coordinates interfaces. The app service wires concrete implementations. UI code calls the app service rather than constructing adapters.

Keep modules focused and small. Non-obvious architecture changes require an ADR under `docs/decisions/`. Do not replace the existing architecture merely to match a different language or framework.

## Research data flow

1. The agent asks the local model to plan a bounded set of queries.
2. Search adapters return result metadata. Provider failures are isolated so other queries can continue.
3. Candidate URLs pass the fetch safety checks. The fetcher applies time and response-size limits, uses the shared retry/diagnostic helper where integrated, and caches extracted page text.
4. The passage splitter stores exact start/end offsets into the canonical page text and a page hash.
5. BM25 ranks the candidate passages. The model receives numbered passage IDs and text excerpts, then selects IDs.
6. The renderer loads the corresponding cached page, verifies its hash and checks that the stored slice still equals the passage text.
7. Only then does it create the displayed quote and its source link. The summary is model-generated and is kept separate from the verified quote text.
8. The complete run is written as an immutable JSON file.

The model does not author quotation text. It chooses passage IDs; deterministic application code reconstructs the quotation from the fetched page text.

## Storage

The user-selected storage root contains separated data, cache, model, log and temporary areas (with assets kept separately where required). Run files are stored under the data area and grouped by project. Cached extracted page text is stored separately and is keyed by URL-derived cache identifiers. Model files and the installed-model registry live under the model area.

Storage migration copies data to the new root, verifies the copy, updates the user configuration and retains the original data. Do not silently delete the old root.

## Networking and privacy

The current fetch implementation validates URLs and blocks private-address targets. The shared network helper provides bounded retries for selected transient errors/statuses, Retry-After handling and redacted JSONL diagnostics. It is integrated with page fetching and Wikipedia search; not every network operation uses the same helper yet.

Permitted online operations are search-provider requests, webpage/robots requests and user-initiated model downloads. Model inference uses a local runtime or localhost endpoint. No cloud AI service is mandatory. The complete requested network-failure test matrix is still outstanding.

## Current limitations and planned boundaries

- The current selection contract is passage-ID based. Sentence-range selection is a later, explicitly gated milestone.
- The current agent loop has bounded planning/search/selection/judgement rounds. The closed-set SEARCH/OPEN/FINISH tool protocol is also gated for a later milestone.
- The Android app is not yet present. The planned Android implementation is Kotlin/Compose with llama.cpp through JNI, using a shared contract to keep behaviour aligned with Python.
- Automatic cross-device sync, memory, RAG, profiles/skills, feedback tuning and advanced settings remain future work.
- Output truncation detection and controlled continuation are not implemented yet.
- Shift+Enter multiline input is not implemented in the current single-line Tk prompt.


# Architecture

This file is the short architecture entry point. The current module map, dependency rules, research data flow, storage model, networking boundaries and known gaps are documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

The architecture is intentionally modular:

- `core` holds portable data models and events.
- `settings` loads and validates configuration and resolves runtime paths.
- `search`, `fetch`, `llm` and `passages` provide replaceable adapters and processing components.
- `agent` coordinates the bounded research loop through interfaces.
- `storage` persists immutable run files.
- `app` composes the implementation behind `ResearchService`.
- `ui` contains the Tk desktop UI and CLI; both call the app facade.

Dependency direction is inward toward portable interfaces: core does not depend on UI or external providers; adapters implement narrow boundaries; the app composes them; UI does not instantiate providers directly.

Do not rewrite the existing architecture to suit a different language. Android will be a separate Kotlin implementation that matches the Python reference through the shared contract planned in `CODEX_NEXT_STEPS.md`.

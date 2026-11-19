# Architecture

`core` contains portable data structures. `settings` loads TOML. Adapters in `llm`, `search` and `fetch` implement narrow interfaces. `passages` splits canonical text, ranks it and verifies exact source offsets. `agent` coordinates bounded research. `storage` persists immutable runs. `app` is the composition and rendering layer; `ui` calls only that facade.

Data flows from question to search hits, fetched page text, exact passage slices, selection, verified quotes, summary and immutable run file. User data is stored under `data/`; cache is URL-hash keyed and logs have a separate configured path. `ResearchService` wires the adapters and is the only API used by UIs.

Dependency direction: `core` is standalone; adapters use core/settings; agent uses interfaces; app wires implementations; UI imports app/core only. Third-party imports belong in adapter modules.

Configuration groups: `[app]` paths/project, `[llm]` active profile, `[search]` provider/results, `[fetch]` network bounds, `[passages]` slicing/ranking, `[agent]` mode and call bounds, `[output]` rendering. Typed dataclasses validate the TOML shape. Model-specific endpoint and generation values live in `config/models.toml`.

Runs are immutable JSON files in `data/projects/<project>/`; extracted page text is cached under `data/cache/` and can be excluded from Syncthing using `data/.stignore.example`.

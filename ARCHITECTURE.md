# Architecture

`core` contains portable data structures. `settings` loads TOML. Adapters in `llm`, `search` and `fetch` implement narrow interfaces. `passages` splits canonical text, ranks it and verifies exact source offsets. `agent` coordinates bounded research. `storage` persists immutable runs. `app` is the composition and rendering layer; `ui` calls only that facade.

Data flows from question to search hits, fetched page text, exact passage slices, selection, verified quotes, summary and immutable run file. User data is stored under `data/`; cache and logs are separate.

Dependency direction: `core` is standalone; adapters use core/settings; agent uses interfaces; app wires implementations; UI imports app/core only. Third-party imports belong in adapter modules.

Configuration groups: `[app]` paths/project, `[llm]` active profile, `[search]` provider/results, `[fetch]` network bounds, `[passages]` slicing/ranking, `[agent]` mode and call bounds, `[output]` rendering. Model-specific endpoint and generation values live in `config/models.toml`.

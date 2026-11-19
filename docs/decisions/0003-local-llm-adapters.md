# 0003: Keep model calls behind an adapter

- Agent steps depend on one small generation interface.
- Ollama uses its native chat endpoint and JSON schema format.
- OpenAI-compatible servers use the common chat completions endpoint.
- The fake backend keeps pipeline tests offline and deterministic.
- Doctor reports connection status without logging prompts or user data.

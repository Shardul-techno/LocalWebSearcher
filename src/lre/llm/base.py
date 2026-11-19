from typing import Any, Protocol


class LLMBackend(Protocol):
    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> str: ...

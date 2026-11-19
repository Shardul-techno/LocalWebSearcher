from typing import Any

from lre.llm.base import LLMBackend
from lre.llm.ollama import OllamaBackend
from lre.llm.openai_compat import OpenAICompatBackend


def build_backend(profile: dict[str, Any]) -> LLMBackend:
    backend = profile["backend"]
    if backend == "ollama":
        return OllamaBackend(profile)
    if backend in {"openai_compat", "llamacpp_managed"}:
        return OpenAICompatBackend(profile)
    raise ValueError(f"Unsupported LLM backend: {backend}")

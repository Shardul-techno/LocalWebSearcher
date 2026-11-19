from typing import Any

import httpx


class OpenAICompatBackend:
    def __init__(self, profile: dict[str, Any]):
        self.profile = profile

    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> str:
        profile = self.profile
        payload: dict[str, Any] = {"model": profile["model"], "messages": [{"role": "user", "content": prompt}], "temperature": profile.get("temperature", 0.1), "max_tokens": profile.get("max_tokens", 300), "stream": False}
        if schema and profile.get("supports_json_schema", False):
            payload["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "schema": schema, "strict": True}}
        response = httpx.post(f"{profile['base_url'].rstrip('/')}/chat/completions", json=payload, timeout=profile.get("timeout_seconds", 120))
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])

from typing import Any

import httpx


class OllamaBackend:
    def __init__(self, profile: dict[str, Any]):
        self.profile = profile

    def generate(self, prompt: str, schema: dict[str, Any] | None = None) -> str:
        profile = self.profile
        payload: dict[str, Any] = {
            "model": profile["model"],
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": profile.get("think", False),
            "options": {"temperature": profile.get("temperature", 0.1), "num_ctx": profile.get("num_ctx", 4096), "num_predict": profile.get("max_tokens", 300)},
        }
        if schema and profile.get("supports_json_schema", False):
            payload["format"] = schema
        response = httpx.post(f"{profile['base_url'].rstrip('/')}/api/chat", json=payload, timeout=profile.get("timeout_seconds", 120))
        response.raise_for_status()
        return str(response.json()["message"]["content"])

    def doctor(self) -> tuple[bool, str]:
        try:
            response = httpx.get(f"{self.profile['base_url'].rstrip('/')}/api/tags", timeout=5)
            response.raise_for_status()
            models = [model.get("name", "") for model in response.json().get("models", [])]
            tag = self.profile["model"]
            if not any(name == tag or name.split(":")[0] == tag.split(":")[0] for name in models):
                return False, f"Model not installed: {tag}"
            self.generate("Reply with exactly: OK")
            return True, f"Ollama ready: {tag}"
        except Exception as exc:
            return False, f"Ollama unavailable: {type(exc).__name__}"

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Settings:
    values: dict[str, Any]
    models: dict[str, dict[str, Any]]

    @property
    def active_model(self) -> dict[str, Any]:
        name = self.values["llm"]["active_model"]
        return self.models[name]

    def section(self, name: str) -> dict[str, Any]:
        return self.values[name]

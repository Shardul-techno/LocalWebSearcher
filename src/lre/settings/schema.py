from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    data_dir: str
    storage_dir: str
    log_dir: str
    default_project: str
    language: str


@dataclass(frozen=True)
class LLMConfig:
    active_model: str


@dataclass(frozen=True)
class SearchConfig:
    provider: str
    results_per_query: int
    region: str
    safe_search: str


@dataclass(frozen=True)
class FetchConfig:
    timeout_seconds: int
    max_bytes: int
    max_pages_per_round: int
    workers: int
    user_agent: str
    block_private_ips: bool
    respect_robots_txt: bool


@dataclass(frozen=True)
class PassageConfig:
    target_chars: int
    max_chars: int
    overlap_sentences: int
    min_chars: int
    top_k_to_model: int
    max_chars_per_passage_in_prompt: int
    stop_words: tuple[str, ...]
    k1: float
    b: float


@dataclass(frozen=True)
class ModeConfig:
    rounds: int
    queries_per_round: int
    pages_per_round: int


@dataclass(frozen=True)
class StyleConfig:
    top_k_to_model: int


@dataclass(frozen=True)
class AgentConfig:
    default_mode: str
    modes: dict[str, ModeConfig]
    styles: dict[str, StyleConfig]
    max_llm_calls_per_run: int
    stop_on_sufficient: bool


@dataclass(frozen=True)
class OutputConfig:
    max_quotes: int
    max_summary_sentences: int


@dataclass(frozen=True)
class TypedSettings:
    app: AppConfig
    llm: LLMConfig
    search: SearchConfig
    fetch: FetchConfig
    passages: PassageConfig
    agent: AgentConfig
    output: OutputConfig


@dataclass(frozen=True)
class Settings:
    values: dict[str, Any]
    models: dict[str, dict[str, Any]]
    typed: TypedSettings

    @property
    def active_model(self) -> dict[str, Any]:
        name = self.values["llm"]["active_model"]
        return self.models[name]

    def section(self, name: str) -> dict[str, Any]:
        return self.values[name]


def make_typed(values: dict[str, Any]) -> TypedSettings:
    agent = values["agent"]
    return TypedSettings(
        AppConfig(**values["app"]), LLMConfig(**values["llm"]), SearchConfig(**values["search"]),
        FetchConfig(**values["fetch"]), PassageConfig(**{**values["passages"], "stop_words": tuple(values["passages"]["stop_words"])}),
        AgentConfig(agent["default_mode"], {key: ModeConfig(**item) for key, item in agent["modes"].items()}, {key: StyleConfig(**item) for key, item in agent["styles"].items()}, agent["max_llm_calls_per_run"], agent["stop_on_sufficient"]),
        OutputConfig(**values["output"]),
    )

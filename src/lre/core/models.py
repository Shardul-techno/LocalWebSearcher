from dataclasses import dataclass, field


@dataclass(frozen=True)
class Passage:
    pid: int
    doc_id: str
    text: str
    start: int
    end: int
    text_hash: str


@dataclass(frozen=True)
class PassageSlice:
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str = ""
    provider: str = ""
    rank: int = 0


@dataclass(frozen=True)
class SourceDoc:
    doc_id: str
    url: str
    title: str
    fetched_at: str
    text_hash: str
    status: str = "ok"
    error: str | None = None


@dataclass(frozen=True)
class RankedPassage:
    passage: Passage
    score: float


@dataclass(frozen=True)
class Selection:
    pids: tuple[int, ...]
    source: str


@dataclass(frozen=True)
class Answer:
    summary: str | None
    summary_status: str
    cited_pids: tuple[int, ...] = ()


@dataclass(frozen=True)
class TraceStep:
    name: str
    started_at: str
    duration_ms: int
    info: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Run:
    schema_version: int
    run_id: str
    project: str
    question: str
    mode: str
    model_profile: str
    created_at: str
    settings_digest: str
    sources: tuple[SourceDoc, ...]
    passages: tuple[Passage, ...]
    selection: Selection
    answer: Answer
    trace: tuple[TraceStep, ...]

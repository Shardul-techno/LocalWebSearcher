from typing import Protocol

from lre.core.models import Passage, RankedPassage


class Ranker(Protocol):
    def rank(self, query: str, passages: list[Passage], limit: int | None = None) -> list[RankedPassage]: ...

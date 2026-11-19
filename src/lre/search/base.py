from typing import Protocol

from lre.core.models import SearchHit


class SearchProvider(Protocol):
    def search(self, query: str, limit: int) -> list[SearchHit]: ...

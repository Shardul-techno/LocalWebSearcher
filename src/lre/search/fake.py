from lre.core.models import SearchHit


class FakeSearchProvider:
    def __init__(self, hits: list[SearchHit]):
        self.hits = hits

    def search(self, query: str, limit: int) -> list[SearchHit]:
        return self.hits[:limit]

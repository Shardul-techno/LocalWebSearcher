from typing import Any

from ddgs import DDGS

from lre.core.models import SearchHit


class DuckDuckGoProvider:
    def __init__(self, region: str = "wt-wt", safe_search: str = "moderate"):
        self.region = region
        self.safe_search = safe_search

    def search(self, query: str, limit: int) -> list[SearchHit]:
        rows: list[dict[str, Any]] = DDGS().text(query, region=self.region, safesearch=self.safe_search, max_results=limit)
        return [SearchHit(row.get("title", ""), row.get("href", ""), row.get("body", ""), "ddg", i) for i, row in enumerate(rows, 1) if row.get("href")]

import httpx

from lre.core.models import SearchHit


class WikipediaProvider:
    def __init__(self, language: str = "en", timeout_seconds: float = 10):
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, limit: int) -> list[SearchHit]:
        response = httpx.get(self.base_url, params={"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": limit}, timeout=self.timeout_seconds, headers={"User-Agent": "lre/0.1 (local research tool)"})
        response.raise_for_status()
        rows = response.json().get("query", {}).get("search", [])
        return [SearchHit(row["title"], f"https://en.wikipedia.org/wiki/{row['title'].replace(' ', '_')}", row.get("snippet", ""), "wikipedia", i) for i, row in enumerate(rows, 1)]

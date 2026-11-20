import httpx

from lre.core.models import SearchHit
from lre.fetch.network import request_with_retry


class WikipediaProvider:
    def __init__(self, language: str = "en", timeout_seconds: float = 10, log_dir=None):
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
        self.timeout_seconds = timeout_seconds
        self.log_dir = log_dir

    def search(self, query: str, limit: int) -> list[SearchHit]:
        params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": limit}
        with httpx.Client(timeout=httpx.Timeout(self.timeout_seconds, connect=min(self.timeout_seconds, 8))) as client:
            response = request_with_retry(client, "GET", self.base_url, params=params,
                                          log_dir=self.log_dir, operation="wikipedia_search")
            try:
                response.raise_for_status()
                rows = response.json().get("query", {}).get("search", [])
                return [SearchHit(row["title"], f"https://en.wikipedia.org/wiki/{row['title'].replace(' ', '_')}",
                                  row.get("snippet", ""), "wikipedia", i) for i, row in enumerate(rows, 1)]
            finally:
                response.close()

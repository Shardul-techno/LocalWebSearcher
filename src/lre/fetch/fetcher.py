import hashlib
from pathlib import Path
from urllib.parse import urljoin

import httpx

from lre.fetch.safety import validate_url


def cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class PageFetcher:
    def __init__(self, extractor, cache_dir: Path, timeout_seconds: float = 15, max_bytes: int = 2_000_000, user_agent: str = "lre/0.1", block_private: bool = True, respect_robots: bool = True):
        self.extractor = extractor
        self.cache_dir = cache_dir
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.user_agent = user_agent
        self.block_private = block_private
        self.respect_robots = respect_robots

    def fetch(self, url: str) -> tuple[str, str]:
        key = cache_key(url)
        cache_file = self.cache_dir / f"{key}.txt"
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8"), key
        validate_url(url, self.block_private)
        headers = {"User-Agent": self.user_agent}
        if self.respect_robots and not self._allowed_by_robots(url, headers):
            raise ValueError("Blocked by robots.txt")
        current = url
        with httpx.Client(timeout=self.timeout_seconds, follow_redirects=False, headers=headers) as client:
            for _ in range(4):
                validate_url(current, self.block_private)
                with client.stream("GET", current) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise ValueError("Redirect without location")
                        current = urljoin(current, location)
                        continue
                    response.raise_for_status()
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > self.max_bytes:
                            raise ValueError("Page exceeds configured size limit")
                    html = bytes(body).decode(response.encoding or "utf-8", errors="replace")
                text = self.extractor.extract(html, current)
                if not text:
                    raise ValueError("No readable page text found")
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(text, encoding="utf-8")
                return text, key
        raise ValueError("Too many redirects")

    def _allowed_by_robots(self, url: str, headers: dict[str, str]) -> bool:
        parts = httpx.URL(url)
        robots_url = f"{parts.scheme}://{parts.host}/robots.txt"
        validate_url(robots_url, self.block_private)
        response = httpx.get(robots_url, timeout=self.timeout_seconds, headers=headers, follow_redirects=False)
        if response.status_code == 404:
            return True
        response.raise_for_status()
        from urllib.robotparser import RobotFileParser
        parser = RobotFileParser(robots_url)
        parser.parse(response.text.splitlines())
        return parser.can_fetch(self.user_agent, url)

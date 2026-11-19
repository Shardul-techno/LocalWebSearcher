from typing import Protocol

import trafilatura


class TextExtractor(Protocol):
    def extract(self, html: str, url: str) -> str: ...


class TrafilaturaExtractor:
    def extract(self, html: str, url: str) -> str:
        return trafilatura.extract(html, url=url, include_comments=False, include_tables=True) or ""

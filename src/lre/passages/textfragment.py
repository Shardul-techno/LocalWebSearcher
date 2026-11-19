import re
from urllib.parse import quote, urlsplit, urlunsplit


def _words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def build(url: str, passage_text: str, whole_text_limit: int = 300, edge_words: int = 6) -> str:
    words = _words(passage_text.strip())
    if not words:
        return url
    def encode(value: str) -> str:
        return quote(value, safe="").replace("-", "%2D")

    if len(passage_text) <= whole_text_limit:
        fragment = encode(" ".join(words))
    else:
        first = " ".join(words[:edge_words])
        last = " ".join(words[-edge_words:])
        fragment = f"{encode(first)},{encode(last)}"
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, f":~:text={fragment}"))

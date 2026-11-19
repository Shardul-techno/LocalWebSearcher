import hashlib

from lre.core.models import Passage


def page_hash(page_text: str) -> str:
    return hashlib.sha256(page_text.encode("utf-8")).hexdigest()


def verify_passage(passage: Passage, page_text: str) -> bool:
    return (
        0 <= passage.start <= passage.end <= len(page_text)
        and page_text[passage.start:passage.end] == passage.text
        and passage.text_hash == page_hash(page_text)
    )

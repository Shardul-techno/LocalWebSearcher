from dataclasses import dataclass

from lre.core.models import PassageSlice


@dataclass(frozen=True)
class SplitConfig:
    target_chars: int = 400
    max_chars: int = 700
    min_chars: int = 80
    overlap_sentences: int = 0


def split(page_text: str, cfg: SplitConfig) -> list[PassageSlice]:
    """Split canonical text without rewriting it; offsets always point into page_text."""
    if not page_text or cfg.max_chars <= 0 or cfg.target_chars <= 0:
        return []
    output: list[PassageSlice] = []
    start = 0
    length = len(page_text)
    while start < length:
        hard_limit = min(start + cfg.max_chars, length)
        target = min(start + cfg.target_chars, hard_limit)
        floor = min(start + cfg.min_chars, hard_limit)
        boundaries = []
        for mark in ("\n\n", ". ", "? ", "! ", "\n", " "):
            pos = page_text.rfind(mark, floor, target + 1)
            if pos >= floor:
                boundaries.append(pos + len(mark))
            pos = page_text.find(mark, target, hard_limit)
            if pos >= 0:
                boundaries.append(pos + len(mark))
        limit = min(boundaries, key=lambda pos: (abs(pos - target), pos)) if boundaries else hard_limit
        end = limit
        while start < end and page_text[start].isspace():
            start += 1
        while end > start and page_text[end - 1].isspace():
            end -= 1
        if end - start >= cfg.min_chars:
            output.append(PassageSlice(page_text[start:end], start, end))
        if limit >= length:
            break
        # Move forward deterministically; overlap is expressed as a small character window
        # behind the prior end so each slice remains an exact source substring.
        next_start = limit
        if cfg.overlap_sentences:
            prior = page_text[start:limit]
            punctuation = [prior.rfind(mark) for mark in (". ", "? ", "! ")]
            cut = max(punctuation)
            if cut >= 0:
                next_start = start + cut
        start = max(start + 1, next_start)
    return output

import math
import re
from collections import Counter

from lre.core.models import Passage, RankedPassage


def _tokens(text: str, stop_words: frozenset[str]) -> list[str]:
    return [word for word in re.findall(r"\w+", text.casefold()) if word not in stop_words]


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75, stop_words: set[str] | None = None):
        self.k1 = k1
        self.b = b
        self.stop_words = frozenset(stop_words or set())

    def rank(self, query: str, passages: list[Passage], limit: int | None = None) -> list[RankedPassage]:
        if not passages:
            return []
        docs = [_tokens(p.text, self.stop_words) for p in passages]
        qterms = set(_tokens(query, self.stop_words))
        avg_len = sum(map(len, docs)) / len(docs) or 1.0
        frequencies = Counter(term for doc in docs for term in set(doc))
        ranked = []
        for passage, words in zip(passages, docs):
            counts = Counter(words)
            score = 0.0
            for term in qterms:
                tf = counts[term]
                if tf:
                    idf = math.log(1 + (len(docs) - frequencies[term] + 0.5) / (frequencies[term] + 0.5))
                    score += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * len(words) / avg_len))
            ranked.append(RankedPassage(passage, score))
        ranked.sort(key=lambda item: (-item.score, item.passage.pid))
        return ranked if limit is None else ranked[:limit]

from lre.core.models import Passage
from lre.passages.splitter import SplitConfig, split
from lre.passages.ranker import BM25
from lre.passages.textfragment import build
from lre.passages.verify import page_hash, verify_passage


def test_split_round_trip_unicode_long_and_duplicate_text():
    page = (("Café 東京 is useful. Repeated sentence. Repeated sentence.\n\n" * 30) + "x" * 80)
    slices = split(page, SplitConfig(target_chars=120, max_chars=150, min_chars=30))
    assert slices
    for index, item in enumerate(slices, 1):
        passage = Passage(index, "doc", item.text, item.start, item.end, page_hash(page))
        assert page[item.start:item.end] == item.text
        assert verify_passage(passage, page)
        assert len(item.text) <= 150


def test_empty_and_short_pages():
    assert split("", SplitConfig()) == []
    assert split("short", SplitConfig(min_chars=20)) == []


def test_text_fragment_golden_and_replaces_existing_fragment():
    assert build("https://example.test/a#old", "Hello, world!") == "https://example.test/a#:~:text=Hello%2C%20world%21"


def test_long_fragment_uses_start_and_end():
    result = build("https://example.test/", " ".join(["one two three four five six seven eight nine ten"] * 7))
    assert ":~:text=one%20two%20three%20four%20five%20six," in result


def test_tampered_text_fails_verification():
    page = "A sufficiently long passage for verification."
    item = split(page, SplitConfig(min_chars=1))[0]
    passage = Passage(1, "doc", item.text, item.start, item.end, "bad")
    assert not verify_passage(passage, page)


def test_bm25_ranks_relevant_passage_first():
    passages = [
        Passage(1, "a", "Oranges grow on trees.", 0, 22, ""),
        Passage(2, "b", "Python is a programming language.", 0, 32, ""),
    ]
    ranked = BM25(stop_words={"is", "a"}).rank("Python programming", passages)
    assert ranked[0].passage.pid == 2
    assert ranked[0].score > ranked[1].score


def test_text_fragment_escapes_hyphen():
    assert "%2D" in build("https://example.test/", "well-known wording")

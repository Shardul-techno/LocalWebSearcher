from pathlib import Path

import pytest

from lre.core.models import SearchHit
from lre.fetch.extract import TrafilaturaExtractor
from lre.fetch.safety import validate_url
from lre.search.fake import FakeSearchProvider


def test_fake_search_is_bounded():
    provider = FakeSearchProvider([SearchHit("a", "https://example.org"), SearchHit("b", "https://example.net")])
    assert len(provider.search("question", 1)) == 1


def test_saved_html_extracts_readable_text():
    fixture = Path(__file__).parent / "fixtures" / "article.html"
    text = TrafilaturaExtractor().extract(fixture.read_text(encoding="utf-8"), "https://example.org")
    assert "reduce peak demand" in text
    assert "Home | About" not in text


@pytest.mark.parametrize("url", ["file:///etc/passwd", "javascript:alert(1)", "http://127.0.0.1/admin"])
def test_unsafe_urls_are_rejected(url):
    with pytest.raises(ValueError):
        validate_url(url)


@pytest.mark.integration
def test_wikipedia_integration():
    from lre.search.wikipedia import WikipediaProvider
    assert WikipediaProvider().search("Python programming language", 1)

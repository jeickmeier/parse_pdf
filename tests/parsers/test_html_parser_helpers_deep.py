import asyncio
from bs4 import BeautifulSoup
import pytest

from doc_parser.config import AppConfig
from doc_parser.parsers.html.parser import HtmlParser


@pytest.fixture()
def parser():
    return HtmlParser(AppConfig())


# ---------------------------------------------------------------------------
# Perplexity page parsing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parse_perplexity_page(parser):
    html = """
    <html><body>
        <h1 class="query">What is AI?</h1>
        <div class="answer">Artificial intelligence answer</div>
        <a class="source" href="https://example.com">Example</a>
        <li class="related">What is ML?</li>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    data = await parser._parse_perplexity_page(soup, "https://perplexity.ai/xyz")  # noqa: SLF001

    assert data["query"].startswith("What is AI")
    assert "Artificial intelligence" in data["answer"]
    assert data["sources"][0]["url"] == "https://example.com"
    assert "What is ML?" in data["related_questions"][0]


@pytest.mark.asyncio
async def test_format_markdown_perplexity(parser):
    content_data = {
        "title": "My Title",
        "query": "Question?",
        "answer": "42",
        "sources": [{"title": "Src", "url": "https://s.com"}],
        "related_questions": ["Related Q"],
        "is_perplexity": True,
        "content_type": "text/html",
    }
    md = await parser._format_as_markdown(content_data, "https://page")  # noqa: SLF001
    assert "## Query" in md and "## Answer" in md and "## Sources" in md
    assert "[Src](https://s.com)" in md


# ---------------------------------------------------------------------------
# General page parsing with links & images
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parse_general_page_links_images(parser):
    parser.follow_links = True  # type: ignore[attr-defined]

    html = """
    <html><body>
      <main>
        <p>Hello world</p>
        <a href="https://link">L</a>
        <img src="img.png" alt="Alt" />
      </main>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    data = await parser._parse_general_page(soup, "https://host")  # noqa: SLF001

    assert "Hello world" in data["content"]
    assert data["links"][0]["url"] == "https://link"
    assert data["images"][0]["src"] == "img.png"

    md = await parser._format_as_markdown(data | {"title": "T", "description": "D", "is_perplexity": False}, "https://host")  # noqa: SLF001
    # Markdown should include link list if follow_links True
    assert "## Links" in md 
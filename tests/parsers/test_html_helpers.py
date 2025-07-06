from bs4 import BeautifulSoup
import pytest
import asyncio

from doc_parser.config import AppConfig
from doc_parser.parsers.html.parser import HtmlParser


@pytest.fixture()
def html_parser() -> HtmlParser:  # noqa: D401
    return HtmlParser(AppConfig())


def test_extract_title_and_description(html_parser: HtmlParser):
    html_doc = """
    <html>
      <head>
        <title>Example Page</title>
        <meta name="description" content="Simple description" />
      </head>
      <body><h1>Heading</h1><p>Text</p></body>
    </html>
    """
    soup = BeautifulSoup(html_doc, "html.parser")
    assert html_parser._extract_title(soup) == "Example Page"  # noqa: SLF001
    assert html_parser._extract_description(soup) == "Simple description"  # noqa: SLF001


@pytest.mark.asyncio
async def test_format_as_markdown_general_page(html_parser: HtmlParser):
    content_data = {
        "title": "My Title",
        "description": "Desc",
        "content": "Some *markdown* content",
        "links": [{"text": "Google", "url": "https://google.com"}],
        "is_perplexity": False,
    }
    # Enable link inclusion
    html_parser.follow_links = True  # type: ignore[attr-defined]
    md = await html_parser._format_as_markdown(content_data, "https://example.com")  # noqa: SLF001
    # Basic assertions on markdown structure
    assert md.startswith("# My Title")
    assert "Some *markdown* content" in md
    assert "[Google](https://google.com)" in md 
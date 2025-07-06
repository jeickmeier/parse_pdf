import asyncio
import plistlib
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from doc_parser.config import AppConfig
from doc_parser.parsers.html.parser import HtmlParser


@pytest.fixture()
def html_parser(tmp_path):  # noqa: D401
    return HtmlParser(AppConfig(cache_dir=tmp_path / "cache"))


# ---------------------------------------------------------------------------
# Title / description fallbacks
# ---------------------------------------------------------------------------


def test_extract_title_description_meta(html_parser):
    html = """
    <html><head>
      <meta property="og:title" content="OG TITLE"/>
      <meta property="og:description" content="OG DESC"/>
    </head><body></body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    assert html_parser._extract_title(soup) == "OG TITLE"  # noqa: SLF001
    assert html_parser._extract_description(soup) == "OG DESC"  # noqa: SLF001


# ---------------------------------------------------------------------------
# .webloc validation & extraction
# ---------------------------------------------------------------------------


def test_validate_and_extract_webloc(tmp_path, html_parser):
    # Build a minimal plist webloc file
    data = {"URL": "https://example.com"}
    raw = plistlib.dumps(data).decode()
    webloc = tmp_path / "link.webloc"
    webloc.write_text(raw)

    assert asyncio.run(html_parser.validate_input(webloc)) is True
    # Protected method usage
    extracted = asyncio.run(html_parser._extract_url(webloc))  # noqa: SLF001
    assert extracted == "https://example.com"


# ---------------------------------------------------------------------------
# format_as_markdown when follow_links False – links section must be absent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_format_markdown_no_links(html_parser):
    html_parser.follow_links = False  # ensure disabled
    data = {
        "title": "T",
        "description": "D",
        "content": "Text",
        "links": [{"text": "L", "url": "https://l"}],
        "images": [],
        "is_perplexity": False,
    }
    md = await html_parser._format_as_markdown(data, "https://h")  # noqa: SLF001
    assert "## Links" not in md


# ---------------------------------------------------------------------------
# parse() of local .url file with mocked fetch
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parse_local_url_file(tmp_path, monkeypatch):
    url_file = tmp_path / "sample.url"
    url_file.write_text("""[InternetShortcut]\nURL=https://host/page\n""")

    async def fake_fetch(self, url: str):  # noqa: D401, ARG002
        return {
            "title": "Title",
            "description": "Desc",
            "content": "Body",
            "links": [],
            "images": [],
            "is_perplexity": False,
            "content_type": "text/html",
        }

    monkeypatch.setattr(
        "doc_parser.parsers.html.parser.HtmlParser._fetch_and_parse", fake_fetch, raising=True
    )

    parser = HtmlParser(AppConfig())
    result = await parser.parse(url_file)
    assert result.metadata["url"].startswith("https://host")
    assert "Body" in result.content 
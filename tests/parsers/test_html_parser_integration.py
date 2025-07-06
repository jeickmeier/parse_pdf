import asyncio
from pathlib import Path
from typing import Any

import pytest

from doc_parser.core.settings import Settings
from doc_parser.parsers.html.parser import HtmlParser


@pytest.fixture()
def html_parser_full(tmp_path):  # noqa: D401
    settings = Settings(use_cache=False, cache_dir=tmp_path / "cache")
    return HtmlParser(settings)


# ---------------------------------------------------------------------------
# Local .url validation & extraction helpers
# ---------------------------------------------------------------------------


def test_validate_and_extract_url(tmp_path, html_parser_full):
    url_file = tmp_path / "link.url"
    url_file.write_text("""[InternetShortcut]\nURL=https://example.com\n""")

    # validate_input should return True
    assert asyncio.run(html_parser_full.validate_input(url_file)) is True

    # _extract_url should return the URL string (protected method)
    extracted = asyncio.run(html_parser_full._extract_url(url_file))  # noqa: SLF001
    assert extracted == "https://example.com"


# ---------------------------------------------------------------------------
# parse() with mocked _fetch_and_parse to avoid HTTP
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parse_url_with_mock(monkeypatch, html_parser_full):
    fake_data = {
        "title": "Mock Page",
        "description": "Desc",
        "content": "Body text",
        "links": [],
        "images": [],
        "is_perplexity": False,
        "content_type": "text/html",
    }

    async def fake_fetch(self, url: str):  # noqa: D401, ARG002
        return fake_data

    monkeypatch.setattr(
        "doc_parser.parsers.html.parser.HtmlParser._fetch_and_parse", fake_fetch, raising=True
    )

    result = await html_parser_full.parse("https://mock.page")
    assert result.metadata["title"] == "Mock Page"
    assert "Body text" in result.content 
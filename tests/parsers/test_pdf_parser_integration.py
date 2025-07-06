import asyncio
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from doc_parser.config import AppConfig
from doc_parser.parsers.pdf.parser import PDFParser
from doc_parser.options import PdfOptions


@pytest.mark.asyncio
async def test_pdf_parser_parse_and_cache(tmp_path, monkeypatch):
    """Parse a dummy PDF (mocked) and verify caching behaviour."""
    # ------------------------------------------------------------------
    # 1. Create a fake PDF file (non-empty so validate_input passes)
    # ------------------------------------------------------------------
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("dummy")

    # ------------------------------------------------------------------
    # 2. Patch pdf2image.convert_from_path to return fake images
    # ------------------------------------------------------------------
    def fake_convert(_path: str, **_kwargs: Any):  # noqa: D401
        # Always return two blank images regardless of kwargs
        return [Image.new("RGB", (10, 10), color="white") for _ in range(2)]

    monkeypatch.setattr(
        "doc_parser.parsers.pdf.parser.convert_from_path", fake_convert, raising=True
    )

    # ------------------------------------------------------------------
    # 3. Patch VisionExtractor.extract so we avoid external API calls
    # ------------------------------------------------------------------
    call_counter: dict[str, int] = {"count": 0}

    async def fake_extract(self, content, prompt_template=None):  # noqa: D401, ARG002
        call_counter["count"] += 1
        if isinstance(content, list):
            # Batch mode -> return numbered pages
            return "\n\n".join(f"Page {i+1}" for i in range(len(content)))
        return "Page 1"

    monkeypatch.setattr(
        "doc_parser.parsers.pdf.parser.VisionExtractor.extract", fake_extract, raising=True
    )

    # ------------------------------------------------------------------
    # 4. Run parser twice – second run should hit cache (extract not called)
    # ------------------------------------------------------------------
    settings = AppConfig(use_cache=True, cache_dir=tmp_path / "cache")
    parser = PDFParser(settings)

    result1 = await parser.parse(pdf_path)
    assert result1.metadata["pages"] == 2
    assert result1.content.startswith("Page 1")

    # Second run – VisionExtractor.extract should *not* be invoked again
    result2 = await parser.parse(pdf_path)
    assert result2.content == result1.content


@pytest.mark.asyncio
async def test_pdf_parser_page_range(tmp_path, monkeypatch):
    """Ensure page_range option limits conversion calls."""
    pdf_path = tmp_path / "range.pdf"
    pdf_path.write_text("x")

    # Fake convert_from_path counts pages requested
    captured_kwargs: dict[str, Any] = {}

    def fake_convert(_path: str, **kwargs: Any):  # noqa: D401
        captured_kwargs.update(kwargs)
        return [Image.new("RGB", (10, 10), color="white")]

    monkeypatch.setattr(
        "doc_parser.parsers.pdf.parser.convert_from_path", fake_convert, raising=True
    )

    async def fake_extract(self, content, prompt_template=None):  # noqa: D401, ARG002
        return "Single Page"

    monkeypatch.setattr(
        "doc_parser.parsers.pdf.parser.VisionExtractor.extract", fake_extract, raising=True
    )

    parser = PDFParser(AppConfig(use_cache=False))
    opts = PdfOptions(page_range=(1, 1))
    _ = await parser.parse(pdf_path, options=opts)

    # convert_from_path should have received first_page / last_page args
    assert captured_kwargs.get("first_page") == 1
    assert captured_kwargs.get("last_page") == 1 
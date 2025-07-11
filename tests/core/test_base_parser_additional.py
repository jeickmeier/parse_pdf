import asyncio
from pathlib import Path
from typing import Any
from pydantic import BaseModel

import pytest

from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.config import AppConfig


class CountingParser(BaseParser):
    """Dummy parser that counts how many times _parse is executed."""

    def __init__(self, settings: AppConfig):
        super().__init__(settings)
        self.call_count = 0

    async def validate_input(self, input_path: Path) -> bool:  # noqa: D401
        return True

    async def _parse(self, input_path: Path, *, options: BaseModel | None = None) -> ParseResult:  # noqa: D401
        _ = options
        self.call_count += 1
        return ParseResult(content="dummy", metadata=self.get_metadata(input_path), output_format=self.settings.output_format)


@pytest.mark.asyncio
async def test_parse_markdown_and_json_wrappers(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")

    parser = CountingParser(AppConfig(use_cache=False))

    md_result = await parser.parse_markdown(file_path)
    assert md_result.content == "dummy"
    assert md_result.output_format == "markdown"

    json_result = await parser.parse_json(file_path)
    assert json_result.content == "dummy"
    assert json_result.output_format == "json"


@pytest.mark.asyncio
async def test_parse_caching(tmp_path):
    file_path = tmp_path / "f.txt"
    file_path.write_text("y")
    settings = AppConfig(use_cache=True, cache_dir=tmp_path / "cache")
    parser = CountingParser(settings)

    # First parse stores in cache
    _ = await parser.parse(file_path)
    assert parser.call_count == 1
    # Second parse should hit cache (call_count unchanged)
    _ = await parser.parse(file_path)
    assert parser.call_count == 1


@pytest.mark.asyncio
async def test_post_processing_success(monkeypatch, tmp_path):
    file_path = tmp_path / "p.txt"
    file_path.write_text("x")

    # Dummy LLM that returns processed content
    class DummyLLM:
        def __init__(self, *_args, **_kwargs):
            pass

        async def process(self, _content: str, _prompt: str):  # noqa: D401
            return "processed"

    # Patch the real LLMPostProcessor with our dummy
    import doc_parser.utils.llm_post_processor as lpp  # noqa: WPS433

    monkeypatch.setattr(lpp, "LLMPostProcessor", DummyLLM, raising=True)

    settings = AppConfig(use_cache=False, post_prompt="Summarize")
    parser = CountingParser(settings)

    result = await parser.parse(file_path)
    assert result.post_content == "processed"
    assert result.errors == []


@pytest.mark.asyncio
async def test_post_processing_failure(monkeypatch, tmp_path):
    file_path = tmp_path / "p2.txt"
    file_path.write_text("x")

    class FailingLLM:
        def __init__(self, *_args, **_kwargs):
            pass

        async def process(self, *_a, **_kw):  # noqa: D401, ANN001
            raise RuntimeError("boom")

    import doc_parser.utils.llm_post_processor as lpp  # noqa: WPS433

    monkeypatch.setattr(lpp, "LLMPostProcessor", FailingLLM, raising=True)

    settings = AppConfig(use_cache=False, post_prompt="Prompt")
    parser = CountingParser(settings)

    with pytest.raises(RuntimeError):
        await parser.parse(file_path) 
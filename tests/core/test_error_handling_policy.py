from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.config import AppConfig
from doc_parser.core.error_policy import EXPECTED_EXCEPTIONS


class DummyParser(BaseParser):
    """A minimal parser used to test the global error-handling policy."""

    def __init__(self, should_raise: Exception | None = None):
        cfg = AppConfig()
        super().__init__(cfg)
        self._should_raise = should_raise

    async def validate_input(self, _input_path: Path) -> bool:  # noqa: D401
        return True

    async def _open_document(self, _input_path: Path, *, options=None):  # noqa: D401
        return object()

    async def _extract_as_markdown(self, _doc):  # noqa: D401
        if self._should_raise:
            raise self._should_raise
        return "sample"

    async def _extract_as_json(self, _doc):  # noqa: D401
        return "{}"


@pytest.mark.asyncio
@pytest.mark.parametrize("exc", [exc() for exc in EXPECTED_EXCEPTIONS])
async def test_expected_exceptions_are_caught(exc, tmp_path):
    """Parsers should convert *expected* errors into ParseResult.errors."""
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("x")
    parser = DummyParser(should_raise=exc)
    result: ParseResult = await parser.parse(dummy_file)
    assert result.errors, "Expected errors list to be populated"
    assert isinstance(result, ParseResult)


@pytest.mark.asyncio
async def test_unexpected_exceptions_propagate(tmp_path):
    """Errors not in EXPECTED_EXCEPTIONS should propagate (fail-fast)."""

    class UnexpectedError(RuntimeError):
        pass

    dummy_file = tmp_path / "d.txt"
    dummy_file.write_text("y")
    parser = DummyParser(should_raise=UnexpectedError())
    with pytest.raises(UnexpectedError):
        await parser.parse(dummy_file) 
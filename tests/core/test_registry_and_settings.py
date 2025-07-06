from pathlib import Path
from typing import Any

import pytest

from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.config import AppConfig
from doc_parser.core.exceptions import UnsupportedFormatError


# ---------------------------------------------------------------------------
# Dummy parser for .txt files (simple in-memory implementation)
# ---------------------------------------------------------------------------

@AppConfig.register("txt", [".txt"])
class TxtParser(BaseParser):
    async def validate_input(self, input_path: Path) -> bool:  # noqa: D401
        return input_path.suffix.lower() == ".txt"

    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:  # noqa: D401
        return ParseResult(content=input_path.read_text(), metadata=self.get_metadata(input_path))


# ---------------------------------------------------------------------------
# Registry behaviour
# ---------------------------------------------------------------------------

def test_registry_from_path(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello")

    parser = AppConfig.from_path(path)
    assert isinstance(parser, TxtParser)


def test_registry_list_and_support(tmp_path):
    # list_parsers should include our 'txt' registration
    parsers_map = AppConfig.list_parsers()
    assert "txt" in parsers_map
    assert ".txt" in parsers_map["txt"]

    # is_supported should reflect that
    txt_file = tmp_path / "file.txt"
    txt_file.write_text("x")
    assert AppConfig.is_supported(txt_file) is True

    # Unsupported extension raises
    unsupported = tmp_path / "file.xyz"
    unsupported.write_text("x")
    with pytest.raises(UnsupportedFormatError):
        AppConfig.from_path(unsupported)


def test_registry_get_parser_by_name():
    parser = AppConfig.get_parser_by_name("txt")
    assert isinstance(parser, TxtParser)


# ---------------------------------------------------------------------------
# Settings model helpers
# ---------------------------------------------------------------------------

def test_settings_path_coercion(tmp_path):
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "out"

    settings = AppConfig(cache_dir=str(cache_dir), output_dir=str(out_dir))

    # Directories should have been created and typed as Path
    assert isinstance(settings.cache_dir, Path) and settings.cache_dir.exists()
    assert isinstance(settings.output_dir, Path) and settings.output_dir.exists()


def test_settings_parser_cfg():
    overrides = {"excel": {"include_formulas": True}}
    settings = AppConfig(parser_settings=overrides)
    assert settings.parser_cfg("excel") == overrides["excel"] 
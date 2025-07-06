from pathlib import Path
from typing import Any

from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.config import AppConfig


class DummyParser(BaseParser):
    async def validate_input(self, input_path: Path) -> bool:  # noqa: D401
        return True

    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:  # noqa: D401
        return ParseResult(content="dummy", metadata=self.get_metadata(input_path))


def test_generate_cache_key(tmp_path):
    file_path = tmp_path / "f.txt"
    file_path.write_text("x")

    parser = DummyParser(AppConfig())
    key1 = parser.generate_cache_key(file_path)

    # Modify file to change mtime
    file_path.write_text("y")
    key2 = parser.generate_cache_key(file_path)

    assert key1 != key2


def test_parse_result_helpers(tmp_path):
    pr = ParseResult(content="abc", metadata={"a": 1})

    # to_dict roundtrip
    d = pr.to_dict()
    assert d["content"] == "abc"

    # to_json returns valid JSON string
    js = pr.to_json()
    assert "\"content\": \"abc\"" in js

    # save_markdown writes to disk
    md_path = tmp_path / "out.md"
    pr.save_markdown(md_path)
    assert md_path.read_text() == "abc" 
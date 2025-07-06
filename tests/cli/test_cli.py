from pathlib import Path

from typer.testing import CliRunner

from doc_parser import cli as dp_cli
from doc_parser.config import AppConfig
from doc_parser.core.base import BaseParser, ParseResult
from pydantic import BaseModel

# Ensure Path is available in annotations for Typer introspection
dp_cli.Path = Path  # type: ignore[attr-defined]

app = dp_cli.app

# Register a lightweight parser for .txt (if not already registered)
@AppConfig.register("txt_cli", [".txt"])
class TxtCliParser(BaseParser):
    async def validate_input(self, input_path: Path) -> bool:  # noqa: D401
        return True

    async def _parse(self, input_path: Path, *, options: BaseModel | None = None):  # noqa: D401
        _ = options
        return ParseResult(content=input_path.read_text(), metadata={})


def test_cli_parse_markdown(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("Hello")

    runner = CliRunner()
    result = runner.invoke(app, [str(sample), "-f", "markdown"])
    assert result.exit_code == 0
    assert "Hello" in result.output 
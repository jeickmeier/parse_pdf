import pandas as pd
from pathlib import Path

from doc_parser.utils.format_helpers import rows_to_markdown, dataframe_to_markdown
from doc_parser.core.base import ParseResult


def test_rows_to_markdown_basic():
    rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    md = rows_to_markdown(rows)
    # Header row and one data row should appear
    assert md.startswith("| Name")
    assert "| Alice | 30 |" in md


def test_rows_to_markdown_escape():
    rows = [["A|B", "C\nD"], ["1", "2"]]
    md = rows_to_markdown(rows)
    # Pipe should be escaped and newline replaced with space
    assert "A\\|B" in md
    assert "C D" in md


def test_dataframe_to_markdown():
    df = pd.DataFrame({"Col1": [1, 2], "Col2": ["a", "b"]})
    md = dataframe_to_markdown(df)
    # Table should start with a Markdown header row
    assert md.startswith("| ")
    # Data rows must be present
    assert "| 1 | a |" in md


def test_dataframe_to_markdown_empty():
    import pandas as pd  # local import to avoid global fixture interference
    empty_df = pd.DataFrame()
    md = dataframe_to_markdown(empty_df)
    assert md == "*No data*"


def test_save_markdown(tmp_path):
    content = "# Title\n\nSample paragraph"
    dest = tmp_path / "sample.md"
    pr = ParseResult(content=content, format="markdown")
    pr.save_markdown(dest)
    assert dest.read_text(encoding="utf-8") == content


# Removed is_supported_file tests since functionality is now handled in parser classes. 
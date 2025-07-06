import pandas as pd
from pathlib import Path

from doc_parser.utils.format_helpers import rows_to_markdown, dataframe_to_markdown
from doc_parser.utils.file_helpers import save_markdown
from doc_parser.utils.file_validators import is_supported_file


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
    save_markdown(content, dest)
    assert dest.read_text(encoding="utf-8") == content


def test_is_supported_file(tmp_path):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_text("dummy")

    txt_path = tmp_path / "doc.txt"
    txt_path.write_text("dummy")

    # Should recognise regardless of leading dot in extension list
    assert is_supported_file(pdf_path, ["pdf"]) is True
    assert is_supported_file(pdf_path, [".pdf"]) is True

    # Unsupported extension should return False
    assert is_supported_file(txt_path, ["pdf", "docx"]) is False 
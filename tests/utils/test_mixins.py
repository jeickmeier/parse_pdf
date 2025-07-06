import pandas as pd

from doc_parser.utils.mixins import DataFrameMarkdownMixin, TableMarkdownMixin
from doc_parser.utils.format_helpers import rows_to_markdown, dataframe_to_markdown


class _DummyTableRow:
    """Simple stub mimicking a table row object with *cells* attribute."""

    def __init__(self, values: list[str]):
        self.cells = [type("Cell", (), {"text": v})() for v in values]


class _DummyTable:
    """Stub table object with a *rows* attribute compatible with TableMarkdownMixin."""

    def __init__(self, rows: list[list[str]]):
        self.rows = [_DummyTableRow(r) for r in rows]


class _DummyTablePptxCell:  # noqa: D401  # type: ignore[pycodestyle]
    def __init__(self, value: str):
        self.text_frame = type("Tx", (), {"text": value})()


class _DummyTableRowPptx:
    def __init__(self, values: list[str]):
        self.cells = [_DummyTablePptxCell(v) for v in values]


class _DummyTablePptx:
    def __init__(self, rows: list[list[str]]):
        self.rows = [_DummyTableRowPptx(r) for r in rows]


class _TableMixinUser(TableMarkdownMixin):
    """Concrete class to expose mixin method for testing."""


class _DFMixinUser(DataFrameMarkdownMixin):
    """Concrete class to expose DataFrameMarkdownMixin for testing."""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_table_markdown_mixin_docx_style() -> None:
    rows = [["A", "B"], ["1", "2"]]
    table = _DummyTable(rows)
    expected = rows_to_markdown(rows)
    assert _TableMixinUser()._table_to_markdown(table) == expected


def test_table_markdown_mixin_pptx_style() -> None:
    rows = [["X", "Y"], ["3", "4"]]
    table = _DummyTablePptx(rows)
    expected = rows_to_markdown(rows)
    assert _TableMixinUser()._table_to_markdown(table) == expected


def test_dataframe_markdown_mixin() -> None:
    df = pd.DataFrame({"Col1": [1, 2], "Col2": [3, 4]})
    expected = dataframe_to_markdown(df)
    assert _DFMixinUser()._dataframe_to_markdown(df) == expected 
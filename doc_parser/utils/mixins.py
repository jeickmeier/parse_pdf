# Reusable mixin classes that provide markdown-conversion helpers.

"""Reusable mixin classes that provide markdown-conversion helpers.

These mixins encapsulate functionality that is duplicated across multiple
parser implementations, allowing us to keep each concrete parser lean while
avoiding copy-pasted helper methods.

Exported mixins:
* TableMarkdownMixin  - provides ``_table_to_markdown`` for python-docx and
  python-pptx table objects.
* DataFrameMarkdownMixin - provides ``_dataframe_to_markdown`` for pandas
  ``DataFrame`` objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from doc_parser.utils.format_helpers import dataframe_to_markdown as _df_to_md, rows_to_markdown

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd

__all__ = [
    "DataFrameMarkdownMixin",
    "TableMarkdownMixin",
]


class TableMarkdownMixin:  # pylint: disable=too-few-public-methods
    """Mixin that converts a table-like object to GitHub-flavored Markdown.

    The mixin defines a single helper method *_table_to_markdown* that concrete
    parsers can call or expose.  It attempts to handle both *python-docx* and
    *python-pptx* table objects:

    * python-docx -> :class:`docx.table.Table` - cell text lives in ``cell.text``
    * python-pptx -> :class:`pptx.table.Table` - cell text lives in
      ``cell.text_frame.text``

    If the table structure does not match either library, we fall back to
    casting the cell value to *str*.
    """

    # The method relies only on public attributes, so type ignorance is fine.
    def _table_to_markdown(self, table: Any) -> str:
        """Return *table* rendered as a Markdown string."""
        rows = _extract_table_rows(table)
        return rows_to_markdown(rows)


class DataFrameMarkdownMixin:  # pylint: disable=too-few-public-methods
    """Mixin that exposes ``_dataframe_to_markdown`` using the shared util."""

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """Convert a pandas DataFrame to Markdown using the shared helper."""
        return _df_to_md(df)


# ---------------------------------------------------------------------------
# Internal helpers (module-level, *not* exported)
# ---------------------------------------------------------------------------


def _extract_table_rows(table: Any) -> list[list[str]]:
    """Extract rows of *table* as a list of string lists.

    Handles **python-docx** and **python-pptx** table APIs.  For other table
    representations, falls back to ``str(cell)`` casts.
    """
    rows: list[list[str]] = []

    # Safe getattr checks to avoid AttributeError
    if hasattr(table, "rows"):
        for row in table.rows:
            cell_texts: list[str] = []
            for cell in row.cells:
                if hasattr(cell, "text_frame") and hasattr(cell.text_frame, "text"):
                    cell_texts.append(cell.text_frame.text.strip())
                elif hasattr(cell, "text"):
                    cell_texts.append(str(cell.text).strip())
                else:
                    cell_texts.append(str(cell).strip())
            rows.append(cell_texts)
    return rows

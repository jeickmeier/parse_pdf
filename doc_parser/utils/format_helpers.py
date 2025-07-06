"""Formatting helpers for converting structured data to Markdown.

This module provides utilities to render rows, DataFrames, and lists into
GitHub-flavored Markdown tables, handling escaping and basic heuristics.

Functions:
    rows_to_markdown(rows: Sequence[Sequence[str]]) -> str
    dataframe_to_markdown(df: pd.DataFrame) -> str

Examples:
    >>> from doc_parser.utils.format_helpers import rows_to_markdown
    >>> rows = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
    >>> print(rows_to_markdown(rows))
    | Name  | Age |
    | ----- | --- |
    | Alice | 30  |
    | Bob   | 25  |
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Sequence

# ---------------------------------------------------------------------------
# Markdown table helpers
# ---------------------------------------------------------------------------


def rows_to_markdown(rows: Sequence[Sequence[str]]) -> str:
    """Convert rows (header + data) into a GitHub-flavored Markdown table.

    The first row in *rows* is treated as the header.

    Args:
        rows (Sequence[Sequence[str]]): List of rows, each a sequence of cell strings.

    Returns:
        str: GitHub-flavored Markdown table.

    Example:
        >>> rows = [["A", "B"], ["1", "2"]]
        >>> print(rows_to_markdown(rows))
        | A | B |
        | - | - |
        | 1 | 2 |
    """
    rows = [list(map(_escape_cell, r)) for r in rows]
    if not rows:
        return ""

    header = rows[0]
    lines: list[str] = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["-" * max(3, len(h)) for h in header]) + " |")

    # Use extend for performance when adding rows
    lines.extend(f"| {' | '.join(row)} |" for row in rows[1:])
    return "\n".join(lines)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a pandas DataFrame as a GitHub-flavored Markdown table.

    Detects header row heuristically and escapes pipe characters.

    Args:
        df (pd.DataFrame): DataFrame to render.

    Returns:
        str: Markdown table string, or '*No data*' if DataFrame is empty.

    Example:
        >>> import pandas as pd
        >>> from doc_parser.utils.format_helpers import dataframe_to_markdown
        >>> df = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
        >>> md = dataframe_to_markdown(df)
        >>> md.startswith("| X | Y |")
        True
    """
    if df.empty:
        return "*No data*"

    # pick header row heuristically: first row with non-nulls
    header_row = 0
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        if all(pd.notna(val) and str(val).strip() for val in row[:5]):
            header_row = i
            break

    if header_row > 0:
        headers = df.iloc[header_row].astype(str).tolist()
        data_df = df.iloc[header_row + 1 :].reset_index(drop=True)
        data_df.columns = headers
    else:
        headers = [f"Column {i + 1}" for i in range(len(df.columns))]
        data_df = df.copy()
        data_df.columns = headers

    rows: list[list[str]] = [headers]
    for _, row in data_df.iterrows():
        cells = ["" if pd.isna(v) else _escape_cell(str(v)) for v in row]
        rows.append(cells)

    return rows_to_markdown(rows)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _escape_cell(text: str) -> str:
    r"""Escape pipe and newline characters inside table cells.

    Args:
        text (str): Cell text to escape.

    Returns:
        str: Escaped text safe for Markdown tables.

    Example:
        >>> from doc_parser.utils.format_helpers import _escape_cell
        >>> _escape_cell("a|b\nc")
        'a\\|b c'
    """
    return text.replace("|", "\\|").replace("\n", " ")

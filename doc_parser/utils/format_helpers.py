"""Formatting helpers shared across parsers.

The goal is to avoid duplicating small DataFrame→Markdown or list→Markdown
transformations in every parser.
"""

from __future__ import annotations

from typing import List, Sequence

import pandas as pd


# ---------------------------------------------------------------------------
# Markdown table helpers
# ---------------------------------------------------------------------------


def rows_to_markdown(rows: Sequence[Sequence[str]]) -> str:  # noqa: D401
    """Convert *rows* (header + data) into a GitHub-flavoured Markdown table.

    The first row is treated as the header.
    """
    rows = [list(map(_escape_cell, r)) for r in rows]
    if not rows:
        return ""

    header = rows[0]
    lines: List[str] = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["-" * max(3, len(h)) for h in header]) + " |")

    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def dataframe_to_markdown(df: pd.DataFrame) -> str:  # noqa: D401
    """Return *df* rendered as a Markdown table (best-effort header detection)."""
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

    rows: List[List[str]] = [headers]
    for _, row in data_df.iterrows():
        cells = ["" if pd.isna(v) else _escape_cell(str(v)) for v in row]
        rows.append(cells)

    return rows_to_markdown(rows)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _escape_cell(text: str) -> str:  # noqa: D401
    """Escape pipes and newlines inside table cells."""
    return text.replace("|", "\\|").replace("\n", " ")

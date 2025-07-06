"""Reusable helpers for basic file validation.

These helpers centralise the repetitive checks found in individual parser
``validate_input`` implementations (file existence & extension checks).
Additional domain-specific validation (e.g. opening a workbook) still lives in
the parser itself.
"""

from pathlib import Path
from typing import Sequence


def is_supported_file(path: Path, extensions: Sequence[str]) -> bool:  # noqa: D401
    """Return *True* iff *path* exists, is a file, and matches *extensions*.

    *extensions* may be provided with or without a leading dot and is compared
    case-insensitively.
    """
    if not path.exists() or not path.is_file():
        return False

    ext = path.suffix.lower()
    for e in extensions:
        e = e.lower()
        if not e.startswith("."):
            e = f".{e}"
        if ext == e:
            return True
    return False

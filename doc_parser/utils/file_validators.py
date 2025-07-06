"""File validation utilities.

Provides helpers for common file validation tasks, such as checking existence,
file type, and extension matching.

Functions:
    is_supported_file(path: Path, extensions: Sequence[str]) -> bool

Examples:
    >>> from pathlib import Path
    >>> from doc_parser.utils.file_validators import is_supported_file
    >>> is_supported_file(Path("data/sample.xlsx"), ["xlsx", ".xls"])
    True
    >>> is_supported_file(Path("data/sample.txt"), ["pdf", "docx"])
    False
"""

from collections.abc import Sequence
from pathlib import Path


def is_supported_file(path: Path, extensions: Sequence[str]) -> bool:
    """Return True if path exists, is a file, and matches one of the extensions.

    *extensions* may be provided with or without a leading dot and is compared
    case-insensitively.

    Args:
        path (Path): Path to check.
        extensions (Sequence[str]): File extensions to match (e.g., ['pdf', '.docx']).

    Returns:
        bool: True if path exists, is a file, and has one of the specified extensions.

    Example:
        >>> from pathlib import Path
        >>> from doc_parser.utils.file_validators import is_supported_file
        >>> is_supported_file(Path("report.pdf"), ["pdf"])
        True
    """
    if not path.exists() or not path.is_file():
        return False

    ext = path.suffix.lower()
    for raw_ext in extensions:
        candidate = raw_ext.lower()
        if not candidate.startswith("."):
            candidate = f".{candidate}"
        if ext == candidate:
            return True
    return False

"""Common type aliases used across the library.

Type Aliases:
    PathLike: Union[str, Path]
        Alias for filesystem path parameters, accepts both string and Path.

Examples:
    >>> from doc_parser.core.types import PathLike
    >>> def read(path: PathLike) -> str:
    ...     from pathlib import Path
    ...
    ...     return Path(path).read_text()
    >>> read("example.txt")
    "Hello"
"""

from pathlib import Path

type PathLike = str | Path

"""Alias for path-like inputs (str or Path).

This alias is used throughout the library for parameters representing
filesystem paths to allow flexible input types.

Examples:
>>> from doc_parser.core.types import PathLike
>>> def save(content: str, output: PathLike) -> None:
...     from pathlib import Path
...     Path(output).write_text(content)
"""

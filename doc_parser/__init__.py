"""
Document Parser Library

A modular, extensible document parsing library supporting multiple formats.
"""

__version__ = "0.1.0"

from .core.config import ParserConfig
from .core.registry import ParserRegistry
from .core.base import BaseParser, ParseResult
from .core.exceptions import ParserError, ConfigurationError

# ---------------------------------------------------------------------------
# Ensure all built-in parsers are imported so they self-register with
# ParserRegistry. This lets users simply `import doc_parser` and immediately
# call `ParserRegistry.get_parser(...)` without manually importing each parser
# module first.
# ---------------------------------------------------------------------------

from . import parsers as _builtin_parsers  # noqa: F401, E402 unused-import

__all__ = [
    "ParserConfig",
    "ParserRegistry",
    "BaseParser",
    "ParseResult",
    "ParserError",
    "ConfigurationError",
]

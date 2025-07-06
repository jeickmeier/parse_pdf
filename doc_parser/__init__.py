"""Document Parser Library.

A modular, extensible document parsing library supporting multiple formats.
"""

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# Ensure all built-in parsers are imported so they self-register with
# AppConfig. This lets users simply `import doc_parser` and immediately
# call `AppConfig.get_parser(...)` without manually importing each parser
# module first.
# ---------------------------------------------------------------------------
from doc_parser.config import AppConfig
from doc_parser.utils import logging_config  # noqa: F401  triggers auto-logging init

from . import parsers as _builtin_parsers  # noqa: F401 unused-import
from .core.base import BaseParser, ParseResult
from .core.exceptions import ConfigurationError, ParserError

__all__ = [
    "AppConfig",
    "BaseParser",
    "ConfigurationError",
    "ParseResult",
    "ParserError",
]

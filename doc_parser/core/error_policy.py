"""Centralised error-handling policy for the doc_parser library.

This module declares *expected* exceptions for each major subsystem so that
parsers can catch only those and let unexpected errors propagate (fail-fast).

The constants are grouped per domain to encourage targeted ``except`` blocks:

* IO-related errors       -> ``EXPECTED_IO_ERRORS``
* Value / type errors     -> ``EXPECTED_VALUE_ERRORS``
* Network / HTTP errors   -> ``EXPECTED_NETWORK_ERRORS``
* PDF-specific errors     -> ``EXPECTED_PDF_ERRORS``
* All combined            -> ``EXPECTED_EXCEPTIONS``

Downstream code should import the narrowest applicable group, e.g.::

    from doc_parser.core.error_policy import EXPECTED_IO_ERRORS

    try:
        with open(path) as fh:
            ...
    except EXPECTED_IO_ERRORS as exc:
        logger.debug("Failed to read %s: %s", path, exc)
        raise

Rationale
---------
Catching *only* well-understood exceptions prevents accidentally hiding real
bugs and helps surface stack traces early in development.  For example, a
``KeyError`` from a dict lookup is likely unintended and should bubble up
instead of being swallowed by a broad ``except Exception`` handler.

The grouping approach avoids sprinkling third-party library imports (e.g.
``aiohttp``) throughout the codebase.  Consumers simply reference the tuple
without caring how it was constructed.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# IO / filesystem related errors
# ---------------------------------------------------------------------------
EXPECTED_IO_ERRORS: tuple[type[Exception], ...] = (
    FileNotFoundError,
    IsADirectoryError,
    PermissionError,
    OSError,  # includes low-level IO errors
)

# ---------------------------------------------------------------------------
# Value / type validation errors
# ---------------------------------------------------------------------------
EXPECTED_VALUE_ERRORS: tuple[type[Exception], ...] = (ValueError,)

# ---------------------------------------------------------------------------
# Network / HTTP related errors - optional import of *aiohttp*
# ---------------------------------------------------------------------------
try:
    import aiohttp

    EXPECTED_NETWORK_ERRORS: tuple[type[Exception], ...] = (aiohttp.ClientError,)
except ModuleNotFoundError:  # pragma: no cover - aiohttp optional
    EXPECTED_NETWORK_ERRORS = ()

# ---------------------------------------------------------------------------
# PDF-specific errors from *pdf2image* (import is optional)
# ---------------------------------------------------------------------------
try:
    from pdf2image.exceptions import (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError,
    )

    EXPECTED_PDF_ERRORS: tuple[type[Exception], ...] = (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError,
    )
except ModuleNotFoundError:  # pragma: no cover - pdf2image optional
    EXPECTED_PDF_ERRORS = ()

# ---------------------------------------------------------------------------
# Aggregate - use when a component deals with multiple subsystems
# ---------------------------------------------------------------------------
EXPECTED_EXCEPTIONS: tuple[type[Exception], ...] = (
    *EXPECTED_IO_ERRORS,
    *EXPECTED_VALUE_ERRORS,
    *EXPECTED_NETWORK_ERRORS,
    *EXPECTED_PDF_ERRORS,
)

__all__: list[str] = [
    "EXPECTED_EXCEPTIONS",
    "EXPECTED_IO_ERRORS",
    "EXPECTED_NETWORK_ERRORS",
    "EXPECTED_PDF_ERRORS",
    "EXPECTED_VALUE_ERRORS",
]

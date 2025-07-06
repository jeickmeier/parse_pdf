"""Central logging utility for *doc_parser*.

The module sets up a sane default logging configuration so that debug logs
emitted by the library (particularly around expected-exception handling) are
visible to the application.

Usage (called automatically)::

    import doc_parser  # logging is already configured

You may override the default level by either:

* Setting the environment variable ``DOC_PARSER_DEBUG=1`` prior to import.
* Calling :pyfunc:`init` manually with ``debug=True`` or a custom level.

The configuration is idempotent - re-invoking :pyfunc:`init` will not add
duplicate handlers.
"""

from __future__ import annotations

import logging
import os
from typing import Any

_DEFAULT_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


def init(*, debug: bool | None = None, level: int | None = None, **basic_cfg: Any) -> None:
    """Initialise root logger with sensible defaults.

    Args:
        debug: If *True*, force :pydata:`logging.DEBUG` level regardless of
            *level*. If *None*, the value of the ``DOC_PARSER_DEBUG`` env var is
            consulted (interpreted as *True* when set to ``"1"``).
        level: Explicit logging level.  Ignored when *debug* is *True*.
        **basic_cfg: Additional keyword arguments forwarded to
            :pyfunc:`logging.basicConfig` (e.g., *format*, *datefmt*).
    """
    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers if already configured
    if root_logger.handlers:
        return

    if debug is None:
        debug = os.getenv("DOC_PARSER_DEBUG", "0") == "1"

    level_to_use = logging.DEBUG if debug else level if level is not None else logging.INFO

    cfg: dict[str, Any] = {
        "level": level_to_use,
        "format": _DEFAULT_FORMAT,
        "force": True,  # override possible prior basicConfig calls
    }
    cfg.update(basic_cfg)
    logging.basicConfig(**cfg)


# ---------------------------------------------------------------------------
# Auto-configure on import (respecting env var)
# ---------------------------------------------------------------------------
init()

__all__: list[str] = ["init"]

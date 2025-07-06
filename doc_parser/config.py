"""Application-wide configuration & parser registry.

This module replaces the legacy ``core.settings`` and ``core.registry`` modules
with a *single* Pydantic-powered configuration object.  All user-tuneable
options live in :class:`AppConfig` while the (previously separate) parser
registration / discovery utilities are provided as **class-methods** on the
same model - giving users **one obvious way to configure and introspect
behaviour**.

Key features
------------
1. Strongly-typed fields validated by *Pydantic v2*.
2. Automatic directory creation for filesystem paths.
3. Built-in parser registry with dynamic ``register`` decorator.
4. Lazy global accessor :pyfunc:`get_config` returning a singleton instance.

Usage example
-------------
>>> from doc_parser.config import get_config, AppConfig
>>> cfg = get_config(parser_settings={"pdf": {"dpi": 200}})
>>> print(cfg.cache_dir)
cache/
>>> AppConfig.list_parsers()
{'pdf': ['.pdf'], 'docx': ['.docx'], ...}
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel, Field, field_validator

from doc_parser.core.exceptions import UnsupportedFormatError

if TYPE_CHECKING:  # pragma: no cover - avoid runtime import cycles
    from collections.abc import Callable

    from doc_parser.core.base import BaseParser

# ---------------------------------------------------------------------------
# AppConfig model
# ---------------------------------------------------------------------------


class AppConfig(BaseModel):
    """Central configuration object **and** parser registry.

    All formerly ad-hoc settings are expressed as strongly-typed fields.  The
    class additionally stores two *class-level* registries mapping parser names
    and file-extensions to their implementing classes.
    """

    # ------------------------------------------------------------------
    # General settings
    # ------------------------------------------------------------------
    cache_dir: Path = Field(default_factory=lambda: Path("cache"))
    output_dir: Path = Field(default_factory=lambda: Path("outputs"))

    max_workers: int = 15
    timeout: int = 60  # seconds
    retry_count: int = 3
    batch_size: int = 1
    use_cache: bool = True

    # ------------------------------------------------------------------
    # Model / LLM settings
    # ------------------------------------------------------------------
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"

    # ------------------------------------------------------------------
    # Output / format settings
    # ------------------------------------------------------------------
    output_format: str = "markdown"

    # ------------------------------------------------------------------
    # Parser-specific overrides & post-processing
    # ------------------------------------------------------------------
    parser_settings: dict[str, dict[str, Any]] = Field(default_factory=dict)

    post_prompt: str | None = None
    response_model: str | None = None  # dotted import path to Pydantic model

    # ------------------------------------------------------------------
    # Internal - class-wide parser registry (shared by all instances)
    # ------------------------------------------------------------------
    _parsers: ClassVar[dict[str, type[BaseParser]]] = {}
    _extensions: ClassVar[dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    @field_validator("cache_dir", "output_dir", mode="before")
    @classmethod
    def _coerce_path_and_mkdir(cls, value: str | Path) -> Path:
        """Ensure the given *value* is a *Path* and create the directory."""
        path = Path(value)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def parser_cfg(self, name: str) -> dict[str, Any]:
        """Return the configuration dictionary for *parser* *name*."""
        return self.parser_settings.get(name, {})

    # Backwards-compatible wrapper for legacy code
    def get_parser_config(self, name: str) -> dict[str, Any]:
        """Alias pointing to :meth:`parser_cfg` (kept for transition period)."""
        return self.parser_cfg(name)

    # ------------------------------------------------------------------
    # Parser-registry methods (class-level) - mirror old ``ParserRegistry`` API
    # ------------------------------------------------------------------
    @classmethod
    def register(cls, name: str, extensions: list[str]) -> Callable[[type[BaseParser]], type[BaseParser]]:
        """Decorator to register a *parser* for given *extensions*.

        Example:
        -------
        >>> from doc_parser.config import AppConfig
        >>> @AppConfig.register("txt", [".txt"])
        ... class TxtParser(BaseParser): ...
        """

        def decorator(parser_cls: type[BaseParser]) -> type[BaseParser]:
            # Runtime import to avoid circular dependency at import-time
            from doc_parser.core.base import BaseParser  # local import

            if not issubclass(parser_cls, BaseParser):
                raise TypeError(f"{parser_cls} must inherit from BaseParser")

            if name in cls._parsers:
                raise ValueError(f"Parser '{name}' already registered")

            cls._parsers[name] = parser_cls

            normalized_exts: list[str] = []
            for raw_ext in extensions:
                ext = raw_ext.lower()
                if not ext.startswith("."):
                    ext = f".{ext}"
                cls._extensions[ext] = name
                normalized_exts.append(ext)

            # Attach supported extensions attribute for convenience / tests
            parser_cls.SUPPORTED_EXTENSIONS = normalized_exts  # type: ignore[attr-defined]
            return parser_cls

        return decorator

    # ------------------------------------------------------------------
    # Parser lookup helpers (factory methods)
    # ------------------------------------------------------------------
    @classmethod
    def from_path(cls, file_path: str | Path, config: AppConfig | None = None) -> BaseParser:
        """Instantiate the appropriate parser for *file_path* (by extension/URL)."""
        from pathlib import Path as _Path  # local import to cut cycles

        # Handle raw strings that might be URLs first
        if isinstance(file_path, str):
            if file_path.startswith(("http://", "https://")):
                parser_name = "html"
                parser_cls = cls._parsers.get(parser_name)
                if parser_cls is None:
                    raise UnsupportedFormatError("HTML parser not registered - cannot handle URL input.")
                return parser_cls(config or get_config())
            file_path = _Path(file_path)

        # Filesystem path handling
        ext = file_path.suffix.lower()
        if ext not in cls._extensions:
            raise UnsupportedFormatError(
                f"No parser found for extension '{ext}'. Supported: {list(cls._extensions.keys())}"
            )

        parser_name = cls._extensions[ext]
        parser_cls = cls._parsers[parser_name]
        return parser_cls(config or get_config())

    @classmethod
    def get_parser_by_name(cls, name: str, config: AppConfig | None = None) -> BaseParser:
        """Instantiate registered parser by *name*."""
        if name not in cls._parsers:
            raise ValueError(f"Parser '{name}' not registered. Available: {list(cls._parsers.keys())}")
        return cls._parsers[name](config or get_config())

    @classmethod
    def list_parsers(cls) -> dict[str, list[str]]:
        """Return mapping of parser names → supported extensions."""
        result: dict[str, list[str]] = {}
        for ext, parser_name in cls._extensions.items():
            result.setdefault(parser_name, []).append(ext)
        return result

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Return *True* if *file_path* (or extension) is handled by a registered parser."""
        return Path(file_path).suffix.lower() in cls._extensions

    # ------------------------------------------------------------------
    # Pydantic model config
    # ------------------------------------------------------------------
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


# ---------------------------------------------------------------------------
# Global singleton helpers
# ---------------------------------------------------------------------------

_config_instance: AppConfig | None = None


def get_config(**overrides: Any) -> AppConfig:
    """Return singleton :class:`AppConfig` instance (creating it on first call).

    Optional keyword arguments override default values **only on the initial
    creation**; subsequent calls ignore *overrides* unless the singleton is
    reset manually (e.g., in test-suites).
    """
    global _config_instance  # noqa: PLW0603 - intentional module-level singleton
    if _config_instance is None:
        _config_instance = AppConfig(**overrides)
    return _config_instance


# Convenience alias so downstream code can still import ``Settings`` directly
Settings = AppConfig

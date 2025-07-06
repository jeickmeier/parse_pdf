"""Unified application settings using Pydantic v2.

This model replaces the legacy ``ParserConfig`` dataclass.  It provides:
1. Type validation & coercion (e.g., ``cache_dir`` can be str or Path).
2. Automatic directory creation for filesystem paths.
3. One canonical place where end-users tweak behaviour or override via env vars in
   later iterations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """Top-level configuration shared by all parsers.

    This Pydantic v2 model centralizes all user-configurable settings:

    Attributes:
        cache_dir (Path): Directory to store cache files. Auto-created on init.
        output_dir (Path): Directory for outputs. Auto-created on init.
        max_workers (int): Maximum number of concurrent workers.
        timeout (int): Request and processing timeout in seconds.
        retry_count (int): Number of retry attempts for failed operations.
        batch_size (int): Default batch size for parsers and extractors.
        use_cache (bool): Enable or disable result caching.
        model_provider (str): LLM provider (e.g., 'openai').
        model_name (str): LLM model name.
        output_format (str): Default output format ('markdown' or 'json').
        parser_settings (Dict[str, Dict[str, Any]]): Parser-specific overrides.
        post_prompt (Optional[str]): Prompt for secondary LLM-based post-processing.
        response_model (Optional[str]): Dotted path for structured response model.

    Examples:
        >>> from doc_parser.core.settings import Settings
        >>> settings = Settings(cache_dir="my_cache", output_format="json", parser_settings={"pdf": {"dpi": 200}})
        >>> print(settings.cache_dir)
        my_cache
        >>> print(settings.get_parser_config("pdf"))
        {'dpi': 200}
    """

    # ---------------------------------------------------------------------
    # Directory settings
    # ---------------------------------------------------------------------
    cache_dir: Path = Field(default_factory=lambda: Path("cache"))
    output_dir: Path = Field(default_factory=lambda: Path("outputs"))

    # ------------------------------------------------------------------
    # Processing settings
    # ------------------------------------------------------------------
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
    # API key is now solely read from the OPENAI_API_KEY environment variable;
    # explicit configuration is deprecated to discourage embedding secrets in
    # code or config files.

    # ------------------------------------------------------------------
    # Output settings
    # ------------------------------------------------------------------
    output_format: str = "markdown"  # FIXME: will be removed in favour of explicit parse methods

    # ------------------------------------------------------------------
    # Parser-specific overrides
    # ------------------------------------------------------------------
    parser_settings: dict[str, dict[str, Any]] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------
    post_prompt: str | None = None
    response_model: str | None = None  # dotted import path to Pydantic model

    # ------------------------------------------------------------------
    # Validators & helpers
    # ------------------------------------------------------------------
    @field_validator("cache_dir", "output_dir", mode="before")
    def _coerce_to_path(cls, v: str | Path) -> Path:  # noqa: N805
        """Ensure *v* is a ``Path`` instance and create directories."""
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def parser_cfg(self, name: str) -> dict[str, Any]:
        """Return the configuration dictionary for the specified parser.

        Args:
            name (str): Registered parser name.

        Returns:
            Dict[str, Any]: Parser-specific settings or an empty dict if none configured.

        Example:
            >>> settings = Settings(parser_settings={"excel": {"include_formulas": True}})
            >>> settings.parser_cfg("excel")
            {'include_formulas': True}
        """
        return self.parser_settings.get(name, {})

    def get_parser_config(self, name: str) -> dict[str, Any]:
        """Alias for parser_cfg for backward compatibility.

        Args:
            name (str): Registered parser name.

        Returns:
            Dict[str, Any]: Same as parser_cfg(name).

        Example:
            >>> settings = Settings(parser_settings={"pdf": {"dpi": 300}})
            >>> settings.get_parser_config("pdf")
            {'dpi': 300}
        """
        return self.parser_cfg(name)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

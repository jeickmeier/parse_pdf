"""Unified application settings using Pydantic v2.

This model replaces the legacy ``ParserConfig`` dataclass.  It provides:
1. Type validation & coercion (e.g., ``cache_dir`` can be str or Path).
2. Automatic directory creation for filesystem paths.
3. One canonical place where end-users tweak behaviour or override via env vars in
   later iterations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """Top-level configuration shared by all parsers."""

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
    output_format: str = (
        "markdown"  # FIXME: will be removed in favour of explicit parse methods
    )

    # ------------------------------------------------------------------
    # Parser-specific overrides
    # ------------------------------------------------------------------
    parser_settings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------
    post_prompt: Optional[str] = None
    response_model: Optional[str] = None  # dotted import path to Pydantic model

    # ------------------------------------------------------------------
    # Validators & helpers
    # ------------------------------------------------------------------
    @field_validator("cache_dir", "output_dir", mode="before")
    def _coerce_to_path(cls, v: str | Path) -> Path:  # noqa: D401
        """Ensure *v* is a ``Path`` instance and create directories."""
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def parser_cfg(self, name: str) -> Dict[str, Any]:
        """Return the sub-config dict for a given *parser* name (may be empty)."""
        return self.parser_settings.get(name, {})

    def get_parser_config(self, name: str) -> Dict[str, Any]:
        """Alias for parser_cfg maintained for backward compatibility."""
        return self.parser_cfg(name)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

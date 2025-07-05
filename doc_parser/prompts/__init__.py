"""Prompt template system for document parsers."""

from pathlib import Path
from .base import PromptTemplate, PromptRegistry

# Automatically load bundled Jinja2 templates that live in the same package
_default_templates_dir = Path(__file__).resolve().parent / "templates"
if _default_templates_dir.exists():
    PromptRegistry.init(_default_templates_dir)

__all__ = [
    "PromptTemplate",
    "PromptRegistry",
]

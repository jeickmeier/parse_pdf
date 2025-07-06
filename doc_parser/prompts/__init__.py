"""Prompt template system for document parsers."""

from pathlib import Path

from .base import PromptRegistry, PromptTemplate

# Automatically load bundled Jinja2 templates that live in the same package
_default_templates_dir = Path(__file__).resolve().parent / "templates"
if _default_templates_dir.exists():
    PromptRegistry.init(_default_templates_dir)

__all__ = [
    "PromptRegistry",
    "PromptTemplate",
]

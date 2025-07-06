"""Prompt template system for document parsers using Jinja2.

This module provides:
- PromptTemplate: Load, render, and manage Jinja2 templates with default variables.
- PromptRegistry: Global registry to register and retrieve named templates.

Examples:
    >>> from doc_parser.prompts.base import PromptTemplate, PromptRegistry
    >>> template = PromptTemplate("Hello {{ name }}!", {"name": "World"})
    >>> print(template.render())
    Hello World!
    >>> PromptRegistry.register("greet", template)
    >>> reg = PromptRegistry.get("greet")
    >>> print(reg.render(name="Alice"))
    Hello Alice!
"""

import json
from pathlib import Path
import re
from typing import Any, ClassVar


# pylint: disable=too-many-instance-attributes
class PromptTemplate:
    """Customizable prompt templates using Jinja2.

    A PromptTemplate wraps a Jinja2 template string with optional default variables,
    enabling rendering with additional context at call time.

    Args:
        template_str (str): Jinja2 template string.
        variables (Optional[Dict[str, Any]]): Default variables for rendering.

    Methods:
        render(**kwargs) -> str: Render the template with combined default and override variables.
        from_file(template_path, variables=None) -> PromptTemplate: Load template from .j2 file with optional JSON vars.
        save(path) -> None: Save template string to file and variables to JSON.

    Examples:
        >>> from doc_parser.prompts.base import PromptTemplate
        >>> tmpl = PromptTemplate("Value: {{ x }}", {"x": 1})
        >>> print(tmpl.render())
        Value: 1
        >>> print(tmpl.render(x=2))
        Value: 2
    """

    def __init__(self, template_str: str, variables: dict[str, Any] | None = None) -> None:
        """Initialize prompt template.

        Args:
            template_str: Jinja2 template string
            variables: Default template variables
        """
        self._template_str: str = template_str
        self.variables: dict[str, Any] = variables or {}

    def render(self, **kwargs: Any) -> str:
        """Render prompt with variables.

        Args:
            **kwargs: Template variables

        Returns:
            Rendered prompt string
        """
        context = {**self.variables, **kwargs}

        # Convert any Jinja2-style placeholders ``{{var}}`` to Python ``{var}``
        fmt_str = re.sub(r"{{\s*(\w+)\s*}}", r"{\1}", self._template_str)

        class _SafeDict(dict[str, str]):
            """dict subclass that returns an empty string for missing keys."""

            def __missing__(self, key: str) -> str:
                """Return empty string for missing *key* to avoid KeyError."""
                return ""

        # Use ``format_map`` so that missing keys default to "" instead of raising
        return fmt_str.format_map(_SafeDict(context))

    @classmethod
    def from_file(cls, template_path: Path, variables: dict[str, Any] | None = None) -> "PromptTemplate":
        """Load a PromptTemplate from a .j2 file, optionally loading default variables from a companion .json file.

        Args:
            template_path (Path): Path to the Jinja2 .j2 template file.
            variables (Optional[Dict[str, Any]]): Default variables, overrides companion JSON if provided.

        Returns:
            PromptTemplate: New instance with template content and variables.

        Example:
            >>> from pathlib import Path
            >>> from doc_parser.prompts.base import PromptTemplate
            >>> tmpl = PromptTemplate.from_file(Path("templates/example.j2"))
            >>> print(tmpl.render())
        """
        with template_path.open() as f:
            template_str = f.read()

        # Load variables from companion JSON file if exists
        var_path = template_path.with_suffix(".json")
        if var_path.exists() and variables is None:
            with var_path.open() as f:
                variables = json.load(f)

        return cls(template_str, variables)

    def save(self, path: Path) -> None:
        """Save the template string to the specified file and its variables to a .json sidecar.

        Args:
            path (Path): File path to save the Jinja2 template string.

        Example:
            >>> t = PromptTemplate("Hi")
            >>> t.save(Path("out.j2"))
        """
        with path.open("w") as f:
            f.write(self._template_str)

        # Save variables if any
        if self.variables:
            var_path = path.with_suffix(".json")
            with var_path.open("w") as f:
                json.dump(self.variables, f, indent=2)


class PromptRegistry:
    """Singleton registry for managing named PromptTemplate instances.

    Provides global lookup and registration of templates loaded at init or dynamically.

    Examples:
        >>> from doc_parser.prompts.base import PromptRegistry, PromptTemplate
        >>> tmpl = PromptTemplate("Test")
        >>> PromptRegistry.register("test", tmpl)
        >>> assert "test" in PromptRegistry.list_templates()
        >>> print(PromptRegistry.get("test").render())
        Test
    """

    _templates: ClassVar[dict[str, PromptTemplate]] = {}
    _template_dir: ClassVar[Path | None] = None

    @classmethod
    def init(cls, template_dir: Path) -> None:
        """Initialize the registry by loading all .j2 templates from a directory.

        Args:
            template_dir (Path): Directory containing .j2 template files.

        Example:
            >>> PromptRegistry.init(Path("templates"))
        """
        cls._template_dir = template_dir
        cls._load_templates()

    @classmethod
    def _load_templates(cls) -> None:
        """Load all templates from template directory."""
        if not cls._template_dir or not cls._template_dir.exists():
            return

        for template_file in cls._template_dir.glob("*.md"):
            name = template_file.stem
            cls._templates[name] = PromptTemplate.from_file(template_file)

    @classmethod
    def register(cls, name: str, template: PromptTemplate) -> None:
        """Register a new PromptTemplate under a given name.

        Args:
            name (str): Unique template identifier.
            template (PromptTemplate): Template to register.
        """
        cls._templates[name] = template

    @classmethod
    def get(cls, name: str) -> PromptTemplate | None:
        """Retrieve a registered PromptTemplate by its name.

        Args:
            name (str): Template identifier.

        Returns:
            Optional[PromptTemplate]: The template if found, else None.
        """
        return cls._templates.get(name)

    @classmethod
    def list_templates(cls) -> list[str]:
        """List all registered template names in the registry.

        Returns:
            List[str]: List of template identifiers.

        Example:
            >>> PromptRegistry.list_templates()
            ['pdf_extraction', 'custom']
        """
        return list(cls._templates.keys())


# ------------------------------------------------------------------
# Public exports
# ------------------------------------------------------------------
__all__ = [
    "PromptRegistry",
    "PromptTemplate",
]

"""Customizable prompt templates for document extraction."""

from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Template
import json


# pylint: disable=too-many-instance-attributes
class PromptTemplate:
    """Customizable prompt templates using Jinja2."""

    def __init__(self, template_str: str, variables: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize prompt template.

        Args:
            template_str: Jinja2 template string
            variables: Default template variables
        """
        self.template: Template = Template(template_str)
        self._template_str: str = template_str
        self.variables: Dict[str, Any] = variables or {}

    def render(self, **kwargs: Any) -> str:
        """
        Render prompt with variables.

        Args:
            **kwargs: Template variables

        Returns:
            Rendered prompt string
        """
        context = {**self.variables, **kwargs}
        return self.template.render(**context)

    @classmethod
    def from_file(
        cls, template_path: Path, variables: Optional[Dict[str, Any]] = None
    ) -> "PromptTemplate":
        """
        Load template from file.

        Args:
            template_path: Path to template file
            variables: Default template variables

        Returns:
            PromptTemplate instance
        """
        with open(template_path, "r") as f:
            template_str = f.read()

        # Load variables from companion JSON file if exists
        var_path = template_path.with_suffix(".json")
        if var_path.exists() and variables is None:
            with open(var_path, "r") as f:
                variables = json.load(f)

        return cls(template_str, variables)

    def save(self, path: Path) -> None:
        """Save template to file."""
        with open(path, "w") as f:
            f.write(self._template_str)

        # Save variables if any
        if self.variables:
            var_path = path.with_suffix(".json")
            with open(var_path, "w") as f:
                json.dump(self.variables, f, indent=2)


class PromptRegistry:
    """Registry for managing prompt templates."""

    _templates: Dict[str, PromptTemplate] = {}
    _template_dir: Optional[Path] = None

    @classmethod
    def init(cls, template_dir: Path) -> None:
        """Initialize registry with template directory."""
        cls._template_dir = template_dir
        cls._load_templates()

    @classmethod
    def _load_templates(cls) -> None:
        """Load all templates from template directory."""
        if not cls._template_dir or not cls._template_dir.exists():
            return

        for template_file in cls._template_dir.glob("*.j2"):
            name = template_file.stem
            cls._templates[name] = PromptTemplate.from_file(template_file)

    @classmethod
    def register(cls, name: str, template: PromptTemplate) -> None:
        """Register a prompt template."""
        cls._templates[name] = template

    @classmethod
    def get(cls, name: str) -> Optional[PromptTemplate]:
        """Get template by name."""
        return cls._templates.get(name)

    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names."""
        return list(cls._templates.keys())

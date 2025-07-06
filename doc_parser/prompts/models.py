"""Core models for the ``doc_parser.prompts`` package.

This module defines :class:`PromptTemplate`, a Pydantic model that replaces the
legacy Jinja2 implementation.  The new design is intentionally lightweight:

* ``template`` - A raw Markdown string that uses Python ``str.format``
  placeholders (e.g. ``"Hello {name}!"``).
* ``input_schema`` - A *Pydantic* model **class** (not instance) that describes
  the variables the template expects. Callers may pass either a mapping or an
  instance of this schema to :py:meth:`PromptTemplate.render`; the data is
  validated automatically.
* ``output_schema`` - An optional Pydantic model **class** describing the
  expected structure of the LLM response.  Use
  :py:meth:`PromptTemplate.validate_output` to parse and validate raw model
  output.

Using Pydantic ensures strict typing and removes any runtime dependency on
Jinja2.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_serializer


class PromptTemplate(BaseModel):
    """A validated, self-describing prompt template."""

    template: str = Field(..., description="Markdown prompt with str.format placeholders.")
    input_schema: type[BaseModel] = Field(..., description="Pydantic model class describing input variables.")
    output_schema: type[BaseModel] | None = Field(
        default=None,
        description="Optional Pydantic model class describing expected LLM output.",
    )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def render(self, data: BaseModel | Mapping[str, Any] | None = None, **kwargs: Any) -> str:
        """Render the template after validating *data* with *input_schema*.

        Parameters
        ----------
        data:
            Either an *instance* of ``input_schema`` or a mapping that can be parsed
            into the schema.  If *None*, an *empty* instance of the schema is created
            (meaning all fields must declare defaults).
        **kwargs:
            Extra keyword-style overrides merged *after* the validated data.  Handy
            for single-use substitutions.

        Returns:
        -------
        str
            The rendered prompt ready to be sent to the LLM.
        """
        # Validate / coerce *data* into the declared schema.
        if data is None:
            parsed = self.input_schema()
        elif isinstance(data, self.input_schema):
            parsed = data
        elif isinstance(data, Mapping):
            parsed = self.input_schema.model_validate(data)
        else:  # pragma: no cover - defensive
            raise TypeError(
                "data must be None, a mapping, or an instance of the declared input_schema",
            )

        context = {**parsed.model_dump(), **kwargs}
        try:
            return self.template.format(**context)
        except KeyError as exc:  # pragma: no cover - helpful error
            raise KeyError(f"Missing template variable: {exc.args[0]}") from exc

    def validate_output(self, raw_output: str) -> str | BaseModel:
        """Validate *raw_output* against ``output_schema`` if configured."""
        if self.output_schema is None:
            return raw_output
        try:
            return self.output_schema.model_validate_json(raw_output)
        except ValidationError:
            # Fallback for plain dictionary / object literals.
            return self.output_schema.model_validate(raw_output)

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_file(
        cls,
        path: str | Path,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel] | None = None,
    ) -> PromptTemplate:
        """Load *template* content from *path*.

        The file is expected to contain UTF-8 encoded text (usually ``.md``).
        """
        content = Path(path).read_text(encoding="utf-8")
        return cls(template=content, input_schema=input_schema, output_schema=output_schema)

    # ------------------------------------------------------------------
    # Model configuration
    # ------------------------------------------------------------------
    model_config = {
        "arbitrary_types_allowed": True,  # Allow BaseModel subclass types
    }

    @model_serializer(mode="plain")
    def _serialise(self) -> dict[str, Any]:
        """Custom serialiser - only *template* is included in JSON output."""
        return {"template": self.template}

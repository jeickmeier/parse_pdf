"""Public interface for prompt templates."""

# Re-export the new **Pydantic v2** implementation
from .models import PromptTemplate

# Legacy *PromptRegistry* has been removed together with the Jinja2 implementation.
__all__: list[str] = [
    "PromptTemplate",
]

"""Content extractors for PDF parsing."""

import base64
from io import BytesIO
from typing import Any, Optional, List, Union
from PIL import Image
from openai import AsyncOpenAI

from ...core.base import BaseExtractor
from ...prompts.base import PromptTemplate
from ...utils.async_helpers import run_with_retry


class VisionExtractor(BaseExtractor):
    """Extract content from images using vision models."""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize vision extractor.

        Args:
            model_name: Vision model to use
            api_key: OpenAI API key
        """
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)

    async def extract(
        self, content: Any, prompt_template: Optional[PromptTemplate] = None
    ) -> str:
        """
        Extract text from image using vision model.

        Args:
            content: PIL Image or list of PIL Images
            prompt_template: Optional custom prompt template

        Returns:
            Extracted text content
        """
        if isinstance(content, list):
            return await self._extract_batch(content, prompt_template)
        else:
            return await self._extract_single(content, prompt_template)

    async def _extract_single(
        self, image: Image.Image, prompt_template: Optional[PromptTemplate] = None
    ) -> str:
        """Extract from single image."""
        prompt = self._get_prompt(prompt_template)

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Call vision API with retry
        response = await run_with_retry(
            self._call_vision_api, prompt, image_base64, max_retries=3
        )

        return str(response.choices[0].message.content)

    async def _extract_batch(
        self,
        images: List[Image.Image],
        prompt_template: Optional[PromptTemplate] = None,
    ) -> str:
        """Extract from batch of images."""
        prompt = self._get_prompt(prompt_template)

        # Convert images to base64
        image_contents = []
        for image in images:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()
            image_contents.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                }
            )

        # Build messages
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}, *image_contents],
            }
        ]

        # Call API
        response = await run_with_retry(
            self.client.chat.completions.create,
            model=self.model_name,
            messages=messages,
            max_tokens=4096,
            max_retries=3,
        )

        return str(response.choices[0].message.content)

    async def _call_vision_api(self, prompt: str, image_base64: str) -> Any:
        """Call OpenAI vision API."""
        return await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )

    def get_default_prompt(self) -> str:
        """Return the default prompt for PDF extraction.

        Instead of hard-coding the prompt here, we load the `pdf_extraction` Jinja
        template that is bundled with the library and registered via
        `PromptRegistry`.  This makes it easy for users to override or extend the
        template without modifying the source code.
        """

        # Local import to avoid potential circular dependencies during package
        # initialisation.
        from ...prompts.base import PromptRegistry  # pylint: disable=import-outside-toplevel

        template = PromptRegistry.get("pdf_extraction")
        if template is None:
            raise ValueError(
                "Default prompt template 'pdf_extraction' not found in PromptRegistry."
            )

        # Render with no extra variables; callers can still supply a
        # PromptTemplate or template name via `prompt_template` to customise the
        # prompt further.
        return template.render()

    def _get_prompt(
        self, prompt_template: Optional[Union["PromptTemplate", str]] = None
    ) -> str:
        """Resolve and return the prompt text to use for extraction."""
        if prompt_template is None:
            return self.get_default_prompt()

        # If the caller provided an actual PromptTemplate instance
        if isinstance(prompt_template, PromptTemplate):
            return prompt_template.render()

        # If a string was provided, try to interpret it as the name of a registered template.
        if isinstance(prompt_template, str):
            try:
                from ...prompts.base import (
                    PromptRegistry,
                )  # Local import to avoid circular deps

                template = PromptRegistry.get(prompt_template)
                if template is not None:
                    return template.render()
            except Exception:
                # Fallback handled below if registry lookup fails
                pass
            # Treat the string itself as the complete prompt text
            return prompt_template

        # Unsupported type
        raise TypeError("prompt_template must be None, a PromptTemplate, or str")

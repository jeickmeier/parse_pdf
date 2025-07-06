"""Content extractors for PDF parsing with AI-based vision models.

This module provides VisionExtractor for extracting text content from images
using OpenAI vision models via the Agents SDK, with support for single- and
batch-mode extraction, custom prompts, and caching integration.

Classes:
    VisionExtractor: Extract text from PIL Images using vision models.

Examples:
    >>> from PIL import Image
    >>> import asyncio
    >>> from doc_parser.parsers.pdf.extractors import VisionExtractor
    >>> extractor = VisionExtractor(model_name="gpt-4o-mini")
    >>> img = Image.open("sample.png")
    >>> text = asyncio.run(extractor.extract(img))
    >>> print(text)
"""

import asyncio
import base64
from io import BytesIO
from typing import Any, Union

from agents import Agent, Runner
from PIL import Image

from doc_parser.core.base import BaseExtractor
from doc_parser.prompts.base import PromptTemplate


class VisionExtractor(BaseExtractor):
    """Extract content from images using vision models.

    Args:
        model_name (str): Name of the vision model (e.g., 'gpt-4o-mini').

    Attributes:
        model_name (str): Vision model identifier used for API calls.

    Examples:
        >>> from PIL import Image
        >>> import asyncio
        >>> from doc_parser.parsers.pdf.extractors import VisionExtractor
        >>> extractor = VisionExtractor("gpt-4o-mini")
        >>> img = Image.open("page.png")
        >>> result = asyncio.run(extractor.extract(img))
        >>> assert isinstance(result, str)
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the vision extractor.

        Args:
            model_name (str): Vision model identifier for the Agents SDK.
        """
        self.model_name = model_name

    async def extract(self, content: Any, prompt_template: PromptTemplate | None = None) -> str:
        """Extract text content from one or more images using vision models.

        Args:
            content (PIL.Image.Image | List[PIL.Image.Image]): Single image or list of images.
            prompt_template (Optional[PromptTemplate | str]): Custom prompt template instance or name.

        Returns:
            str: Extracted text content, concatenated with two newlines for batches.

        Example:
            >>> from PIL import Image
            >>> import asyncio
            >>> extractor = VisionExtractor()
            >>> img = Image.open("page.png")
            >>> text = asyncio.run(extractor.extract(img))
        """
        if isinstance(content, list):
            return await self._extract_batch(content, prompt_template)
        else:
            return await self._extract_single(content, prompt_template)

    async def _extract_single(self, image: Image.Image, prompt_template: PromptTemplate | None = None) -> str:
        """Extract text from a single image.

        Args:
            image (PIL.Image.Image): Single page image.
            prompt_template (Optional[PromptTemplate | str]): Custom prompt template or name.

        Returns:
            str: Extracted text for the image.

        Example:
            >>> text = asyncio.run(extractor._extract_single(img))
        """
        prompt = self._get_prompt(prompt_template)

        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Directly call the vision model through the Agents SDK
        return await self._call_vision_api(prompt, image_base64)

    async def _extract_batch(
        self,
        images: list[Image.Image],
        prompt_template: PromptTemplate | None = None,
    ) -> str:
        """Extract text from a batch of images.

        Args:
            images (List[PIL.Image.Image]): List of page images.
            prompt_template (Optional[PromptTemplate | str]): Custom prompt template or name.

        Returns:
            str: Extracted text content for all images, joined by two newlines.

        Example:
            >>> text = asyncio.run(extractor._extract_batch([img1, img2]))
        """
        # Simply fan-out to `_extract_single` for each page and join the results.
        tasks = [self._extract_single(img, prompt_template) for img in images]
        results: list[str] = await asyncio.gather(*tasks)
        return "\n\n".join(results)

    async def _call_vision_api(self, prompt: str, image_base64: str) -> str:
        """Call the OpenAI vision API via the Agents SDK.

        Args:
            prompt (str): Prompt text to send to the model.
            image_base64 (str): Base64-encoded PNG image data.

        Returns:
            str: Raw output from the vision model.

        Raises:
            Exception: If the API call fails.

        Example:
            >>> out = await extractor._call_vision_api("prompt", base64str)
        """
        # Use the Agents SDK to run an ad-hoc Agent that performs the extraction.
        agent = Agent(
            name="VisionExtractor",
            instructions=(
                "You are a vision model that extracts text from images following the"
                " provided instructions. Respond with *only* the extracted markdown "
                "content—no additional commentary."
            ),
            model=self.model_name,
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{image_base64}",
                        "detail": "low",
                    },
                ],
            }
        ]

        result = await Runner.run(agent, messages)  # type: ignore[arg-type]
        return str(result.final_output)

    def get_default_prompt(self) -> str:
        """Load and return the default Jinja2 prompt for PDF vision extraction.

        Returns:
            str: Rendered default prompt template.

        Raises:
            ValueError: If the default 'pdf_extraction' template is not registered.

        Example:
            >>> prompt = extractor.get_default_prompt()
        """
        # Local import to avoid potential circular dependencies during package
        # initialisation.
        from doc_parser.prompts.base import PromptRegistry  # pylint: disable=import-outside-toplevel

        template = PromptRegistry.get("pdf_extraction")
        if template is None:
            raise ValueError("Default prompt template 'pdf_extraction' not found in PromptRegistry.")

        # Render with no extra variables; callers can still supply a
        # PromptTemplate or template name via `prompt_template` to customise the
        # prompt further.
        return template.render()

    def _get_prompt(self, prompt_template: Union["PromptTemplate", str] | None = None) -> str:
        """Resolve and return the prompt text for extraction.

        Args:
            prompt_template (Optional[PromptTemplate | str]): PromptTemplate instance, registered name, or literal prompt.

        Returns:
            str: Final prompt text to send to the model.

        Raises:
            TypeError: If prompt_template is not None, a PromptTemplate, or str.

        Example:
            >>> prompt = extractor._get_prompt("pdf_extraction")
        """
        if prompt_template is None:
            return self.get_default_prompt()

        # If the caller provided an actual PromptTemplate instance
        if isinstance(prompt_template, PromptTemplate):
            return prompt_template.render()

        # If a string was provided, try to interpret it as the name of a registered template.
        if isinstance(prompt_template, str):
            try:
                from doc_parser.prompts.base import PromptRegistry  # Local import to avoid circular deps

                template = PromptRegistry.get(prompt_template)
                if template is not None:
                    return template.render()
            except ImportError:
                # Fallback handled below if registry lookup fails
                pass
            # Treat the string itself as the complete prompt text
            return prompt_template

        # Unsupported type
        raise TypeError("prompt_template must be None, a PromptTemplate, or str")

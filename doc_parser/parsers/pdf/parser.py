"""PDF parser implementation."""

from __future__ import annotations
import asyncio
from pathlib import Path
from typing import List, Optional, Tuple, TYPE_CHECKING, Any
from pdf2image import convert_from_path
from PIL import Image
from tqdm.asyncio import tqdm

from ...core.base import BaseParser, ParseResult
from ...core.registry import ParserRegistry
from ...core.config import ParserConfig
from ...utils.async_helpers import RateLimiter
from .extractors import VisionExtractor

if TYPE_CHECKING:
    from ...prompts.base import PromptTemplate


@ParserRegistry.register("pdf", [".pdf"])
class PDFParser(BaseParser):
    """Enhanced PDF parser with modular design."""

    def __init__(self, config: ParserConfig):
        """
        Initialize PDF parser.

        Args:
            config: Parser configuration
        """
        super().__init__(config)

        # Get PDF-specific settings
        pdf_config = config.get_parser_config("pdf")
        self.dpi = pdf_config.get("dpi", 300)
        self.batch_size = pdf_config.get("batch_size", config.batch_size)

        # Initialize extractor
        self.extractor = VisionExtractor(
            model_name=config.model_name, api_key=config.api_key
        )

        # Rate limiter for API calls
        self.rate_limiter = RateLimiter(config.max_workers)

    async def validate_input(self, input_path: Path) -> bool:
        """Validate if the input file is a valid PDF."""
        if not input_path.exists():
            return False

        if input_path.suffix.lower() != ".pdf":
            return False

        # Check if file is readable and not empty
        try:
            if input_path.stat().st_size == 0:
                return False
            return True
        except Exception:
            return False

    async def parse(self, input_path: Path, **kwargs: Any) -> ParseResult:
        """
        Parse PDF document.

        Args:
            input_path: Path to PDF file
            **kwargs: Additional options (e.g., page_range, prompt_template)

        Returns:
            ParseResult with extracted content
        """
        # Validate input
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid PDF file: {input_path}"],
            )

        # Get options
        page_range = kwargs.get("page_range")
        prompt_template = kwargs.get("prompt_template")

        # Convert PDF to images
        images = await self._pdf_to_images(input_path, page_range)

        # Process pages
        results = await self._process_pages(images, input_path, prompt_template)

        # Combine results
        content = self._combine_results(results)

        # Build metadata
        metadata = self.get_metadata(input_path)
        metadata.update(
            {
                "pages": len(images),
                "dpi": self.dpi,
                "model": self.config.model_name,
            }
        )

        return ParseResult(
            content=content, metadata=metadata, format=self.config.output_format
        )

    async def _pdf_to_images(
        self, pdf_path: Path, page_range: Optional[Tuple[int, int]] = None
    ) -> List[Image.Image]:
        """Convert PDF pages to images."""
        kwargs = {
            "dpi": self.dpi,
            "fmt": "png",
            "thread_count": 4,
        }

        if page_range:
            kwargs["first_page"] = page_range[0]
            kwargs["last_page"] = page_range[1]

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        images = await loop.run_in_executor(
            None, lambda: convert_from_path(str(pdf_path), **kwargs)
        )

        return images

    async def _process_pages(
        self,
        images: List[Image.Image],
        pdf_path: Path,
        prompt_template: Optional["PromptTemplate"] = None,
    ) -> List[str]:
        """Process pages in batches."""
        results = []

        # Create batches
        batches = []
        for i in range(0, len(images), self.batch_size):
            batch = images[i : i + self.batch_size]
            page_nums = list(range(i + 1, i + len(batch) + 1))
            batches.append((batch, page_nums))

        # Process batches concurrently
        tasks = []
        for batch_images, page_nums in batches:
            task = self._process_batch(
                batch_images, page_nums, pdf_path, prompt_template
            )
            tasks.append(task)

        # Execute with progress bar
        batch_results = await tqdm.gather(*tasks, desc=f"Processing {pdf_path.name}")

        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)

        return results

    async def _process_batch(
        self,
        images: List[Image.Image],
        page_nums: List[int],
        pdf_path: Path,
        prompt_template: Optional["PromptTemplate"] = None,
    ) -> List[str]:
        """Process a batch of images."""
        results = []

        async with self.rate_limiter:
            # Check cache for each page
            cached_pages = []
            pages_to_process = []

            for i, (image, page_num) in enumerate(zip(images, page_nums)):
                cache_key = f"{pdf_path.stem}_page_{page_num}"
                cached = await self.cache.get(cache_key)

                if cached:
                    cached_pages.append((i, cached["content"]))
                else:
                    pages_to_process.append((i, image, page_num))

            # Process uncached pages
            if pages_to_process:
                if len(pages_to_process) == 1:
                    # Single page
                    i, image, page_num = pages_to_process[0]
                    content = await self.extractor.extract(image, prompt_template)

                    # Cache result
                    await self.cache.set(
                        f"{pdf_path.stem}_page_{page_num}",
                        {"content": content, "page": page_num},
                    )

                    results.append((i, content))
                else:
                    # Multiple pages
                    indices = [p[0] for p in pages_to_process]
                    images_to_process = [p[1] for p in pages_to_process]
                    page_numbers = [p[2] for p in pages_to_process]

                    content = await self.extractor.extract(
                        images_to_process, prompt_template
                    )

                    # Split content by some delimiter if needed
                    # For now, treat as single result
                    for idx, page_num in zip(indices, page_numbers):
                        # Cache each page
                        await self.cache.set(
                            f"{pdf_path.stem}_page_{page_num}",
                            {"content": content, "page": page_num},
                        )

                    results.append((indices[0], content))

            # Add cached results
            results.extend(cached_pages)

            # Sort by original index
            results.sort(key=lambda x: x[0])

            return [content for _, content in results]

    def _combine_results(self, results: List[str]) -> str:
        """Combine extracted results into final content."""
        # Join with double newlines
        combined = "\n\n".join(results)

        # Clean up any artifacts
        lines = combined.split("\n")
        cleaned_lines: List[str] = []

        for line in lines:
            # Skip empty lines at document boundaries
            if not line.strip() and (
                not cleaned_lines or not cleaned_lines[-1].strip()
            ):
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

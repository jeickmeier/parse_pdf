"""PDF parser implementation.

This module provides a parser for PDF documents that converts pages to images,
extracts text using vision models, and assembles structured output.

Features:
- Convert PDF pages to images via pdf2image
- Single and batch page extraction with async concurrency
- Caching of page results to avoid redundant extraction
- Rate limiting of API calls for controlled concurrency
- Integration with OpenAI vision models via VisionExtractor
- Configurable options: dpi, batch_size, page_range, prompt_template, output_format
- Metadata enrichment: page count, dpi, model name

Example:
>>> import asyncio
>>> from pathlib import Path
>>> from doc_parser.parsers.pdf.parser import PDFParser
>>> from doc_parser.core.settings import Settings
>>> settings = Settings(output_format="markdown", parser_settings={"pdf": {"dpi": 200, "batch_size": 2}})
>>> parser = PDFParser(settings)
>>> result = asyncio.run(parser.parse(Path("sample.pdf")))
>>> print(result.metadata["pages"], result.metadata["dpi"])
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from pdf2image import convert_from_path
from tqdm.asyncio import tqdm

from doc_parser.config import AppConfig
from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.utils.async_batcher import RateLimiter
from doc_parser.utils.cache import cache_get, cache_set

from .extractors import VisionExtractor

if TYPE_CHECKING:
    from pathlib import Path

    from PIL import Image

    from doc_parser.prompts import PromptTemplate


@AppConfig.register("pdf", [".pdf"])
class PDFParser(BaseParser):
    """Parser for PDF documents using image-based extraction.

    Converts PDF pages into images and extracts text via vision models,
    supporting caching and rate limiting for efficiency.

    Args:
        config (Settings): Global parser configuration.

    Attributes:
        dpi (int): Image resolution for conversion.
        batch_size (int): Number of pages per extraction batch.
        extractor (VisionExtractor): Vision-based text extractor.
        rate_limiter (RateLimiter): Controls concurrent API calls.

    Examples:
        >>> import asyncio
        >>> from pathlib import Path
        >>> from doc_parser.parsers.pdf.parser import PDFParser
        >>> from doc_parser.core.settings import Settings
        >>> settings = Settings(parser_settings={"pdf": {"dpi": 300}})
        >>> parser = PDFParser(settings)
        >>> result = asyncio.run(parser.parse(Path("doc.pdf"), page_range=(1, 3)))
        >>> print(result.content[:100])
    """

    def __init__(self, config: AppConfig):
        """Initialize PDF parser with configuration.

        Args:
            config (Settings): Parser configuration object.
        """
        super().__init__(config)

        # Get PDF-specific settings
        pdf_config = config.get_parser_config("pdf")
        self.dpi = pdf_config.get("dpi", 300)
        self.batch_size = pdf_config.get("batch_size", config.batch_size)

        # Initialize extractor
        self.extractor = VisionExtractor(model_name=config.model_name)

        # Rate limiter for API calls
        self.rate_limiter = RateLimiter(config.max_workers)

    async def validate_input(self, input_path: Path) -> bool:
        """Validate whether the input path points to a non-empty PDF file.

        Args:
            input_path (Path): Path to the PDF file.

        Returns:
            bool: True if file exists, has .pdf extension, and is non-empty.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> result = asyncio.run(PDFParser(Settings()).validate_input(Path("file.pdf")))
            >>> print(result)
        """
        if not self._has_supported_extension(input_path):
            return False
        # Check if file is readable and not empty
        try:
            size = input_path.stat().st_size
        except OSError:
            return False
        return size != 0

    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:
        """Parse a PDF document and return extraction results.

        Orchestrates validation, image conversion, text extraction,
        result combination, and metadata construction.

        Args:
            input_path (Path): Path to the PDF file.
            **_kwargs: Additional options:
                page_range (tuple[int, int]): Range of pages to process.
                prompt_template (PromptTemplate|str): Custom prompt template.

        Returns:
            ParseResult: Contains content, metadata, output format, and errors.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = PDFParser(Settings())
            >>> result = asyncio.run(parser.parse(Path("sample.pdf"), page_range=(1, 2)))
            >>> print(result.metadata["pages"])
        """
        # Validate input
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=[f"Invalid PDF file: {input_path}"],
            )

        # Get options
        page_range = _kwargs.get("page_range")
        prompt_template = _kwargs.get("prompt_template")

        # Convert PDF to images
        images = await self._pdf_to_images(input_path, page_range)

        # Process pages
        results = await self._process_pages(images, input_path, prompt_template)

        # Combine results
        content = self._combine_results(results)

        # Build metadata
        metadata = self.get_metadata(input_path)
        metadata.update({
            "pages": len(images),
            "dpi": self.dpi,
            "model": self.settings.model_name,
        })

        return ParseResult(content=content, metadata=metadata, output_format=self.settings.output_format)

    async def _pdf_to_images(self, pdf_path: Path, page_range: tuple[int, int] | None = None) -> list[Image.Image]:
        """Convert PDF pages to PIL Image objects.

        Args:
            pdf_path (Path): Path to the PDF document.
            page_range (Optional[tuple[int, int]]): Inclusive range of pages to process.

        Returns:
            List[Image.Image]: List of page images.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> images = asyncio.run(PDFParser(Settings())._pdf_to_images(Path("doc.pdf"), (1, 2)))
            >>> print(len(images))
        """
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
        images = await loop.run_in_executor(None, lambda: convert_from_path(str(pdf_path), **kwargs))

        return images

    async def _process_pages(
        self,
        images: list[Image.Image],
        pdf_path: Path,
        prompt_template: PromptTemplate | None = None,
    ) -> list[str]:
        """Process page images asynchronously in batches with caching.

        Args:
            images (List[Image.Image]): List of page images.
            pdf_path (Path): Path to the source PDF.
            prompt_template (Optional[PromptTemplate]): Custom prompt or template.

        Returns:
            List[str]: Extracted text per page in original order.

        Example:
            >>> import asyncio
            >>> imgs = asyncio.run(PDFParser(Settings())._pdf_to_images(Path("doc.pdf")))
            >>> texts = asyncio.run(PDFParser(Settings())._process_pages(imgs, Path("doc.pdf")))
        """
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
            task = self._process_batch(batch_images, page_nums, pdf_path, prompt_template)
            tasks.append(task)

        # Execute with progress bar
        batch_results = await tqdm.gather(*tasks, desc=f"Processing {pdf_path.name}")

        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)

        return results

    async def _process_batch(
        self,
        images: list[Image.Image],
        page_nums: list[int],
        pdf_path: Path,
        prompt_template: PromptTemplate | None = None,
    ) -> list[str]:
        """Extract content for a batch of pages and cache results.

        Args:
            images (List[Image.Image]): Subset of page images.
            page_nums (List[int]): Corresponding page numbers.
            pdf_path (Path): Source PDF path.
            prompt_template (Optional[PromptTemplate]): Custom prompt template.

        Returns:
            List[str]: Extracted content strings for the batch.

        Example:
            >>> import asyncio
            >>> result = asyncio.run(PDFParser(Settings())._process_batch([img], [1], Path("doc.pdf")))
        """
        async with self.rate_limiter:
            cached_pages, pages_to_process = await self._get_cached_pages(images, page_nums, pdf_path)

            new_results = await self._process_uncached_pages(pages_to_process, pdf_path, prompt_template)

            # Combine and sort all results to original order
            all_results = cached_pages + new_results
            all_results.sort(key=lambda tpl: tpl[0])  # sort by original index

            # Return only the extracted content
            return [content for _, content in all_results]

    # ------------------------------------------------------------------
    # Helper split-out methods to simplify _process_batch logic
    # ------------------------------------------------------------------

    async def _get_cached_pages(
        self,
        images: list[Image.Image],
        page_nums: list[int],
        pdf_path: Path,
    ) -> tuple[list[tuple[int, str]], list[tuple[int, Image.Image, int]]]:
        """Retrieve cached pages and identify pages requiring extraction.

        Args:
            images (List[Image.Image]): Page images.
            page_nums (List[int]): Page numbers for each image.
            pdf_path (Path): Source PDF path.

        Returns:
            Tuple[
                List[Tuple[int,str]],           # (index, cached_content)
                List[Tuple[int,Image.Image,int]] # (index, image, page_num)
            ]

        Example:
            >>> import asyncio
            >>> cache, to_process = asyncio.run(PDFParser(Settings())._get_cached_pages(imgs, [1], Path("doc.pdf")))
        """
        cached_pages: list[tuple[int, str]] = []
        pages_to_process: list[tuple[int, Image.Image, int]] = []

        for i, (image, page_num) in enumerate(zip(images, page_nums, strict=False)):
            cache_key = f"{pdf_path.stem}_page_{page_num}"
            cached = await cache_get(self.cache, cache_key)
            if cached:
                cached_pages.append((i, cached["content"]))
            else:
                pages_to_process.append((i, image, page_num))

        return cached_pages, pages_to_process

    async def _process_uncached_pages(
        self,
        pages_to_process: list[tuple[int, Image.Image, int]],
        pdf_path: Path,
        prompt_template: PromptTemplate | None,
    ) -> list[tuple[int, str]]:
        """Extract text for uncached pages and update cache.

        Args:
            pages_to_process (List[Tuple[int,Image.Image,int]]): Pages to extract.
            pdf_path (Path): PDF file path.
            prompt_template (Optional[PromptTemplate]): Extraction prompt.

        Returns:
            List[Tuple[int,str]]: List of (index, content) tuples.

        Example:
            >>> import asyncio
            >>> uncached = asyncio.run(PDFParser(Settings())._process_uncached_pages(to_process, Path("doc.pdf"), None))
        """
        if not pages_to_process:
            return []

        results: list[tuple[int, str]] = []

        if len(pages_to_process) == 1:
            # Single page optimisation
            idx, image, page_num = pages_to_process[0]
            content = await self.extractor.extract(image, prompt_template)
            await cache_set(
                self.cache,
                f"{pdf_path.stem}_page_{page_num}",
                {"content": content, "page": page_num},
            )
            results.append((idx, content))
            return results

        # Multiple pages: batch extract
        indices = [tpl[0] for tpl in pages_to_process]
        images = [tpl[1] for tpl in pages_to_process]
        page_numbers = [tpl[2] for tpl in pages_to_process]

        content = await self.extractor.extract(images, prompt_template)

        # TODO: If the extractor ever returns separate strings per page, split here.
        for _idx, page_num in zip(indices, page_numbers, strict=False):
            await cache_set(
                self.cache,
                f"{pdf_path.stem}_page_{page_num}",
                {"content": content, "page": page_num},
            )
        results.append((indices[0], content))

        return results

    def _combine_results(self, results: list[str]) -> str:
        """Clean and combine page extraction results into a single string.

        Joins page texts with double newlines and removes duplicate blank lines.

        Args:
            results (List[str]): List of page text strings.

        Returns:
            str: Final combined content.

        Example:
            >>> combined = PDFParser(Settings())._combine_results(["text1", "", "text2"])
        """
        # Join with double newlines
        combined = "\n\n".join(results)

        # Clean up any artifacts
        lines = combined.split("\n")
        cleaned_lines: list[str] = []

        for line in lines:
            # Skip empty lines at document boundaries
            if not line.strip() and (not cleaned_lines or not cleaned_lines[-1].strip()):
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _has_supported_extension(self, input_path: Path) -> bool:
        """Check if the input path has a supported file extension.

        Args:
            input_path (Path): Path to the file.

        Returns:
            bool: True if the file has a supported extension, False otherwise.
        """
        return super()._has_supported_extension(input_path)

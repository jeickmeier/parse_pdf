#!/usr/bin/env python3
# mypy: ignore-errors

"""Example usage of the document parser library.

This script is illustrative and not part of the library's typed public API,
so we opt out of strict mypy checking to avoid polluting CI results.
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from doc_parser import parsers  # noqa: F401
from doc_parser.config import AppConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info("Loading environment variables from {%s}", Path(__file__).resolve().parent.parent / ".env")
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

logger.info("OPENAI_API_KEY: {%s},", os.getenv("OPENAI_API_KEY"))

async def example_basic_usage():
    """Basic usage example."""
    # Create configuration
    config = AppConfig(
        max_workers=10,
        model_name="gpt-4.1-mini",
        output_format="markdown",
        parser_settings={"pdf": {"dpi": 300, "batch_size": 1}},
        use_cache=False,
    )

    # Parse a PDF file (using the existing hello.py as test)
    pdf_path = Path(
        "/Users/joneickmeier/Documents/Papers Library/Monteggia-The best way forward-2014-Nature.pdf"
    )
    if pdf_path.exists():
        try:
            parser = AppConfig.from_path(pdf_path, config)
            result = await parser.parse(pdf_path)


            # Save to markdown file via ParseResult convenience method
            output_path = Path("outputs") / f"{pdf_path.stem}_parsed.md"
            result.save_markdown(output_path)

        except Exception:
            pass



async def example_html_usage():
    """Example usage of HTML parser to parse a URL."""
    # Create configuration
    config = AppConfig(
        max_workers=10, model_name="gpt-4.1-mini", output_format="markdown"
    )

    url = "https://www.theglobeandmail.com/"

    try:
        parser = AppConfig.from_path(url, config)
        # Directly parse the URL without creating any temporary files
        result = await parser.parse(url)


        # Save to markdown file
        # Construct a safe filename from the URL to avoid invalid path characters
        safe_url = url.replace("/", "_").replace(":", "_")
        output_path = Path("outputs") / f"{safe_url}_parsed.md"
        result.save_markdown(output_path)

    except Exception:
        pass



async def main():
    """Run all examples."""
    await example_basic_usage()
    await example_html_usage()



if __name__ == "__main__":
    asyncio.run(main())

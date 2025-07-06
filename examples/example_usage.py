#!/usr/bin/env python3
# mypy: ignore-errors

"""Example usage of the document parser library.

This script is illustrative and not part of the library's typed public API,
so we opt out of strict mypy checking to avoid polluting CI results.
"""

import asyncio
from pathlib import Path
from doc_parser.core.settings import Settings
from doc_parser.core.registry import ParserRegistry
from doc_parser import parsers  # noqa: F401
from doc_parser.utils import save_markdown


async def example_basic_usage():
    """Basic usage example."""
    print("=== Basic PDF Parsing ===")

    # Create configuration
    config = Settings(
        max_workers=10, 
        model_name="gpt-4.1-mini", 
        output_format="markdown",
        parser_settings={
            "pdf": {
                "dpi": 300,
                "batch_size": 1
            }
        }
    )

    # Parse a PDF file (using the existing hello.py as test)
    pdf_path = Path(
        "/Users/joneickmeier/Documents/Papers Library/Monteggia-The best way forward-2014-Nature.pdf"
    )
    if pdf_path.exists():
        try:
            parser = ParserRegistry.from_path(pdf_path, config)
            result = await parser.parse(pdf_path)

            print(f"Parsed {pdf_path.name}:")
            print(f"Content length: {len(result.content)} characters")
            print(f"Metadata: {result.metadata}")
            print(f"Errors: {result.errors}")

            # Save to markdown file using helper
            output_path = Path("outputs") / f"{pdf_path.stem}_parsed.md"
            save_markdown(result.content, output_path)

            print(f"Saved output to: {output_path}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n")


async def example_html_usage():
    """Example usage of HTML parser to parse a URL."""
    print("=== HTML (Web URL) Parsing ===")

    # Create configuration
    config = Settings(
        max_workers=10, 
        model_name="gpt-4.1-mini", 
        output_format="markdown"
    )

    url = "https://www.theglobeandmail.com/"

    try:
        parser = ParserRegistry.from_path(url, config)
        # Directly parse the URL without creating any temporary files
        result = await parser.parse(url)

        print(f"Parsed {url}:")
        print(f"Content length: {len(result.content)} characters")
        print(f"Metadata: {result.metadata}")
        print(f"Errors: {result.errors}")

        # Save to markdown file
        # Construct a safe filename from the URL to avoid invalid path characters
        safe_url = url.replace("/", "_").replace(":", "_")
        output_path = Path("outputs") / f"{safe_url}_parsed.md"
        save_markdown(result.content, output_path)

        print(f"Saved output to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n")


async def main():
    """Run all examples."""
    print("Document Parser Library Examples\n")

    await example_basic_usage()
    await example_html_usage()

    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

"""HTML parser implementation for web content and Perplexity.ai exports.

This module provides the HtmlParser, capable of parsing:
- Local HTML files with caching and content-type handling
- .url and .webloc link files
- Remote URLs via HTTP/HTTPS
- Perplexity.ai query/answer pages with specialized extraction

Features:
- Caching to disk
- Configurable source extraction, link following, depth limits
- Output formats: Markdown or JSON

Examples:
>>> import asyncio
>>> from doc_parser.core.settings import Settings
>>> from doc_parser.parsers.html.parser import HtmlParser
>>> settings = Settings(parser_settings={"html": {"extract_sources": True, "follow_links": False}})
>>> parser = HtmlParser(settings)
>>> result = asyncio.run(parser.parse("https://example.com"))
>>> print(result.content[:100])
"""

from __future__ import annotations

import plistlib
import re
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag
import html2text

from doc_parser.core.base import BaseParser, ParseResult
from doc_parser.core.registry import ParserRegistry

if TYPE_CHECKING:
    from pathlib import Path

    from doc_parser.core.settings import Settings

MIN_RELATED_LEN = 10


@ParserRegistry.register("html", [".html", ".htm", ".pplx", ".url", ".webloc"])
class HtmlParser(BaseParser):
    """Parser for HTML pages, Perplexity.ai exports, and generic web content.

    This parser handles:
    - Validating and parsing local link files (.url, .webloc)
    - Fetching and parsing HTTP/HTTPS URLs
    - Specialized extraction for Perplexity.ai query/answer pages
    - Configurable extraction of sources and link following
    - Output in Markdown or JSON formats

    Args:
        config (Settings): Global settings with optional 'html' parser config:
            - extract_sources (bool): Include link sources (default True)
            - follow_links (bool): Follow embedded links (default False)
            - max_depth (int): Maximum link-following depth (default 1)

    Examples:
        >>> import asyncio
        >>> from doc_parser.core.settings import Settings
        >>> from doc_parser.parsers.html.parser import HtmlParser
        >>> settings = Settings(parser_settings={"html": {"follow_links": True, "max_depth": 2}})
        >>> parser = HtmlParser(settings)
        >>> result = asyncio.run(parser.parse("example.url"))
        >>> assert "## Links" in result.content
    """

    def __init__(self, config: Settings):
        """Initialize HTML parser with configuration."""
        super().__init__(config)

        html_cfg = config.get_parser_config("html")
        self.extract_sources: bool = html_cfg.get("extract_sources", True)
        self.follow_links: bool = html_cfg.get("follow_links", False)
        self.max_depth: int = html_cfg.get("max_depth", 1)

        # HTML→Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0

    # ------------------------------------------------------------------
    # Public high-level entry-point override to support URL strings
    # ------------------------------------------------------------------
    async def parse(self, input_path: Path | str, **_kwargs: Any) -> ParseResult:
        """Parse input_path as local file or remote URL.

        Overrides BaseParser.parse to route HTTP/HTTPS inputs to parse_url
        and use caching for local files.

        Args:
            input_path (Path | str): File path or URL string.
            **_kwargs: Parser-specific options.

        Returns:
            ParseResult: Parsed content, metadata, format, and errors.

        Example:
            >>> import asyncio
            >>> from doc_parser.core.settings import Settings
            >>> from doc_parser.parsers.html.parser import HtmlParser
            >>> parser = HtmlParser(Settings())
            >>> result = asyncio.run(parser.parse("http://example.com"))
        """
        # Handle URL strings directly
        if isinstance(input_path, str) and input_path.startswith(("http://", "https://")):
            return await self.parse_url(input_path, **_kwargs)

        # Otherwise use the base implementation (expects Path)
        from pathlib import Path as _Path

        if isinstance(input_path, str):
            input_path = _Path(input_path)

        return await super().parse(input_path, **_kwargs)

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------
    async def validate_input(self, input_path: Path) -> bool:
        """Validate whether input_path is a valid URL file (.url/.webloc) with an embedded URL.

        Args:
            input_path (Path): Path to link file.

        Returns:
            bool: True if file exists, is readable, and contains a valid URL.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = HtmlParser(Settings())
            >>> valid = asyncio.run(parser.validate_input(Path("link.url")))
            >>> print(valid)
        """
        if not input_path.exists():
            return False
        # Read file content, return False on I/O or decode errors
        try:
            content = input_path.read_text().strip()
        except (OSError, UnicodeError):
            return False
        # Check for URLs directly in content
        if content.startswith(("http://", "https://")):
            return bool(urlparse(content).netloc)
        if input_path.suffix == ".webloc":
            return "<key>URL</key>" in content
        if input_path.suffix == ".url":
            return "[InternetShortcut]" in content
        return False

    # ------------------------------------------------------------------
    # Public entry-points
    # ------------------------------------------------------------------
    async def _parse(self, input_path: Path, **_kwargs: Any) -> ParseResult:
        """Parse a local URL file and delegate to parse_url.

        Args:
            input_path (Path): Path to .url or .webloc file.
            **_kwargs: Parser-specific options.

        Returns:
            ParseResult: Result of parse_url or error if validation fails.

        Example:
            >>> import asyncio
            >>> from pathlib import Path
            >>> parser = HtmlParser(Settings())
            >>> result = asyncio.run(parser._parse(Path("link.url")))
        """
        if not await self.validate_input(input_path):
            return ParseResult(
                content="",
                metadata=self.get_metadata(input_path),
                errors=["Invalid URL file"],
            )
        url = await self._extract_url(input_path)
        return await self.parse_url(url, **_kwargs)

    async def parse_url(self, url: str, **_kwargs: Any) -> ParseResult:
        """Fetch and parse a remote URL, returning structured ParseResult.

        Args:
            url (str): HTTP/HTTPS URL to fetch.
            **_kwargs: Parser-specific options.

        Returns:
            ParseResult: Parsed content in Markdown or JSON, metadata, and errors.

        Example:
            >>> import asyncio
            >>> parser = HtmlParser(Settings())
            >>> result = asyncio.run(parser.parse_url("http://example.com"))
            >>> print(result.metadata["domain"])
        """
        try:
            content_data = await self._fetch_and_parse(url)
            if self.settings.output_format == "json":
                import json as _json

                content_str = _json.dumps(content_data, indent=2, ensure_ascii=False)
            else:
                content_str = await self._format_as_markdown(content_data, url)

            metadata = {
                "url": url,
                "parser": self.__class__.__name__,
                "title": content_data.get("title", ""),
                "domain": urlparse(url).netloc,
                "content_type": content_data.get("content_type", ""),
            }
            return ParseResult(
                content=content_str,
                metadata=metadata,
                format=self.settings.output_format,
            )
        except (TimeoutError, aiohttp.ClientError, ValueError) as exc:  # pragma: no cover
            return ParseResult(content="", metadata={"url": url}, errors=[str(exc)])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _extract_url(self, input_path: Path) -> str:
        """Extract URL string from link file.

        Args:
            input_path (Path): Path to .url or .webloc file.

        Returns:
            str: Extracted URL string.

        Raises:
            ValueError: If URL cannot be extracted.

        Example:
            >>> url = HtmlParser(Settings())._extract_url(Path("link.url"))
        """
        content = input_path.read_text().strip()
        if content.startswith(("http://", "https://")):
            return content

        if input_path.suffix == ".webloc":
            try:
                plist = plistlib.loads(content.encode())
                return str(plist.get("URL", ""))
            except (plistlib.InvalidFileException, ValueError):
                match = re.search(r"<string>(https?://[^<]+)</string>", content)
                if match:
                    return str(match.group(1))

        if input_path.suffix == ".url":
            match = re.search(r"URL=(https?://[^\r\n]+)", content)
            if match:
                return str(match.group(1))

        raise ValueError("Could not extract URL from file")

    async def _fetch_and_parse(self, url: str) -> dict[str, Any]:
        """Fetch HTML content from URL and parse into data dictionary.

        Args:
            url (str): URL to fetch.

        Returns:
            Dict[str, Any]: Parsed data including title, description, content segments.

        Example:
            >>> import asyncio
            >>> data = asyncio.run(HtmlParser(Settings())._fetch_and_parse("http://example.com"))
            >>> print(data["title"])
        """
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp,
        ):
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            html_content = await resp.text()

        soup = BeautifulSoup(html_content, "html.parser")
        title = self._extract_title(soup)
        description = self._extract_description(soup)

        is_perplexity = "perplexity.ai" in url
        if is_perplexity:
            data = await self._parse_perplexity_page(soup, url)
        else:
            data = await self._parse_general_page(soup, url)

        data.update({
            "title": title,
            "description": description,
            "content_type": content_type,
            "is_perplexity": is_perplexity,
        })
        return data

    # ---------------- specific page handlers ----------------------------
    async def _parse_perplexity_page(self, soup: BeautifulSoup, _url: str) -> dict[str, Any]:
        """Parse a Perplexity.ai page, extracting query, answer, sources, and related questions.

        Args:
            soup (BeautifulSoup): Parsed HTML soup of page.
            _url (str): Original page URL.

        Returns:
            Dict[str, Any]: Contains 'query', 'answer', 'sources', 'related_questions'.

        Example:
            >>> data = asyncio.run(HtmlParser(Settings())._parse_perplexity_page(soup, url))
            >>> assert "query" in data
        """
        data: dict[str, Any] = {
            "query": "",
            "answer": "",
            "sources": [],
            "related_questions": [],
        }

        query_elem = soup.find(["h1", "div"], class_=re.compile(r"query|question", re.I))
        if query_elem:
            data["query"] = query_elem.get_text(strip=True)

        answer_elem = soup.find(["div", "section"], class_=re.compile(r"answer|response|content", re.I))
        if answer_elem:
            data["answer"] = self.h2t.handle(str(answer_elem))
        else:
            main_content = soup.find(["main", "article", "div"], class_=re.compile(r"main|content", re.I))
            if main_content:
                data["answer"] = self.h2t.handle(str(main_content))

        if self.extract_sources:
            sources: list[dict[str, str]] = []
            for elem in soup.find_all(["a", "div"], class_=re.compile(r"source|reference|citation", re.I)):
                if not isinstance(elem, Tag):
                    continue
                href = str(elem.get("href", ""))
                if href.startswith("http"):
                    sources.append({"url": href, "title": elem.get_text(strip=True)})
            data["sources"] = sources

        for elem in soup.find_all(["div", "li"], class_=re.compile(r"related|suggestion", re.I)):
            txt = elem.get_text(strip=True)
            if txt and len(txt) > MIN_RELATED_LEN:
                data["related_questions"].append(txt)
        return data

    async def _parse_general_page(self, soup: BeautifulSoup, _url: str) -> dict[str, Any]:
        """Parse a general HTML page, extracting content, links, and images.

        Args:
            soup (BeautifulSoup): Parsed HTML soup of page.
            _url (str): Original page URL (for link resolution).

        Returns:
            Dict[str, Any]: Contains 'content', optional 'links', and 'images'.

        Example:
            >>> data = asyncio.run(HtmlParser(Settings())._parse_general_page(soup, url))
            >>> assert "content" in data
        """
        data: dict[str, Any] = {"content": "", "links": [], "images": []}

        for script in soup(["script", "style"]):
            script.decompose()

        main_content = None
        for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break
        if not main_content:
            main_content = soup.body or soup

        data["content"] = self.h2t.handle(str(main_content))

        if self.follow_links:
            links: list[dict[str, str]] = []
            for link in main_content.find_all("a", href=True):
                if not isinstance(link, Tag):
                    continue
                href = str(link.get("href", ""))
                if href.startswith("http"):
                    links.append({"url": href, "text": link.get_text(strip=True)})
            data["links"] = links[:20]

        images: list[dict[str, str]] = []
        for img in main_content.find_all("img", src=True):
            if not isinstance(img, Tag):
                continue
            images.append({"src": str(img.get("src", "")), "alt": str(img.get("alt", ""))})
        data["images"] = images[:10]
        return data

    # ---------------- markdown formatter -------------------------------
    async def _format_as_markdown(self, content_data: dict[str, Any], url: str) -> str:
        """Format parsed HTML data into Markdown.

        Builds a Markdown document with title, URL, description, separators, and sections.

        Args:
            content_data (Dict[str, Any]): Data dict returned by parsing helpers.
            url (str): Original URL string.

        Returns:
            str: Markdown-formatted string.

        Example:
            >>> md = asyncio.run(HtmlParser(Settings())._format_as_markdown(data, url))
            >>> print(md.startswith("#"))
        """
        parts: list[str] = []
        if content_data.get("title"):
            parts.append(f"# {content_data['title']}")
        parts.append(f"**URL:** {url}")
        if content_data.get("description"):
            parts.append(f"\n*{content_data['description']}*")
        parts.append("\n---\n")

        if content_data.get("is_perplexity"):
            if content_data.get("query"):
                parts.append(f"## Query\n\n{content_data['query']}")
            if content_data.get("answer"):
                parts.append(f"## Answer\n\n{content_data['answer']}")
            if content_data.get("sources") and self.extract_sources:
                parts.append("## Sources\n")
                for i, src in enumerate(content_data["sources"], 1):
                    parts.append(f"{i}. [{src['title']}]({src['url']})")
            if content_data.get("related_questions"):
                parts.append("\n## Related Questions\n")
                parts.extend(f"- {q}" for q in content_data["related_questions"])
        else:
            if content_data.get("content"):
                parts.append(content_data["content"])
            if content_data.get("links") and self.follow_links:
                parts.append("\n## Links\n")
                parts.extend(f"- [{link['text']}]({link['url']})" for link in content_data["links"][:10])
        return "\n\n".join(parts)

    # ---------------- utility extractors -------------------------------
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from HTML soup.

        Checks <title>, then <meta property='og:title'>, then first <h1>, fallback empty.

        Args:
            soup (BeautifulSoup): Parsed HTML soup.

        Returns:
            str: Page title or empty string.

        Example:
            >>> title = HtmlParser(Settings())._extract_title(soup)
        """
        title_tag = soup.find("title")
        if isinstance(title_tag, Tag):
            return title_tag.get_text(strip=True)
        meta_title = soup.find("meta", property="og:title")
        if isinstance(meta_title, Tag) and meta_title.get("content"):
            return str(meta_title.get("content"))
        h1 = soup.find("h1")
        if isinstance(h1, Tag):
            return h1.get_text(strip=True)
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description from HTML soup.

        Checks <meta name='description'> then <meta property='og:description'>, fallback empty.

        Args:
            soup (BeautifulSoup): Parsed HTML soup.

        Returns:
            str: Page description or empty string.

        Example:
            >>> desc = HtmlParser(Settings())._extract_description(soup)
        """
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if isinstance(meta_desc, Tag) and meta_desc.get("content"):
            return str(meta_desc.get("content"))
        og_desc = soup.find("meta", property="og:description")
        if isinstance(og_desc, Tag) and og_desc.get("content"):
            return str(og_desc.get("content"))
        return ""

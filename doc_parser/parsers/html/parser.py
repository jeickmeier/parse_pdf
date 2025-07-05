"""HTML parser implementation for web content extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import re
from urllib.parse import urlparse

import aiohttp
import html2text
from bs4 import BeautifulSoup
from bs4.element import Tag

from ...core.base import BaseParser, ParseResult
from ...core.registry import ParserRegistry
from ...core.config import ParserConfig


@ParserRegistry.register("html", [".html", ".htm", ".pplx", ".url", ".webloc"])
class HtmlParser(BaseParser):
    """Parser for HTML pages, Perplexity exports, and generic web content."""

    def __init__(self, config: ParserConfig):
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

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------
    async def validate_input(self, input_path: Path) -> bool:
        """Return True if *input_path* contains a valid URL or link file."""
        if not input_path.exists():
            return False

        try:
            content = input_path.read_text().strip()
            if content.startswith(("http://", "https://")):
                return bool(urlparse(content).netloc)

            if input_path.suffix == ".webloc":
                return "<key>URL</key>" in content
            if input_path.suffix == ".url":
                return "[InternetShortcut]" in content
            return False
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Public entry-points
    # ------------------------------------------------------------------
    async def parse(self, input_path: Path, **kwargs: Any) -> ParseResult:
        if not await self.validate_input(input_path):
            return ParseResult("", self.get_metadata(input_path), errors=["Invalid URL file"])
        url = await self._extract_url(input_path)
        return await self.parse_url(url, **kwargs)

    async def parse_url(self, url: str, **kwargs: Any) -> ParseResult:
        """Parse an arbitrary URL and return a ParseResult."""
        try:
            content_data = await self._fetch_and_parse(url)
            if self.config.output_format == "json":
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
            return ParseResult(content_str, metadata, self.config.output_format)
        except Exception as exc:  # pragma: no cover
            return ParseResult("", {"url": url}, errors=[str(exc)])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _extract_url(self, input_path: Path) -> str:
        content = input_path.read_text().strip()
        if content.startswith(("http://", "https://")):
            return content

        if input_path.suffix == ".webloc":
            import plistlib

            try:
                plist = plistlib.loads(content.encode())
                return str(plist.get("URL", ""))
            except Exception:
                match = re.search(r"<string>(https?://[^<]+)</string>", content)
                if match:
                    return str(match.group(1))

        if input_path.suffix == ".url":
            match = re.search(r"URL=(https?://[^\r\n]+)", content)
            if match:
                return str(match.group(1))

        raise ValueError("Could not extract URL from file")

    async def _fetch_and_parse(self, url: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
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
    async def _parse_perplexity_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {"query": "", "answer": "", "sources": [], "related_questions": []}

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
            sources: List[Dict[str, str]] = []
            for elem in soup.find_all(["a", "div"], class_=re.compile(r"source|reference|citation", re.I)):
                if not isinstance(elem, Tag):
                    continue
                href = str(elem.get("href", ""))
                if href.startswith("http"):
                    sources.append({"url": href, "title": elem.get_text(strip=True)})
            data["sources"] = sources

        for elem in soup.find_all(["div", "li"], class_=re.compile(r"related|suggestion", re.I)):
            txt = elem.get_text(strip=True)
            if txt and len(txt) > 10:
                data["related_questions"].append(txt)
        return data

    async def _parse_general_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {"content": "", "links": [], "images": []}

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
            links: List[Dict[str, str]] = []
            for link in main_content.find_all("a", href=True):
                if not isinstance(link, Tag):
                    continue
                href = str(link.get("href", ""))
                if href.startswith("http"):
                    links.append({"url": href, "text": link.get_text(strip=True)})
            data["links"] = links[:20]

        images: List[Dict[str, str]] = []
        for img in main_content.find_all("img", src=True):
            if not isinstance(img, Tag):
                continue
            images.append({"src": str(img.get("src", "")), "alt": str(img.get("alt", ""))})
        data["images"] = images[:10]
        return data

    # ---------------- markdown formatter -------------------------------
    async def _format_as_markdown(self, content_data: Dict[str, Any], url: str) -> str:
        parts: List[str] = []
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
                for q in content_data["related_questions"]:
                    parts.append(f"- {q}")
        else:
            if content_data.get("content"):
                parts.append(content_data["content"])
            if content_data.get("links") and self.follow_links:
                parts.append("\n## Links\n")
                for link in content_data["links"][:10]:
                    parts.append(f"- [{link['text']}]({link['url']})")
        return "\n\n".join(parts)

    # ---------------- utility extractors -------------------------------
    def _extract_title(self, soup: BeautifulSoup) -> str:
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
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if isinstance(meta_desc, Tag) and meta_desc.get("content"):
            return str(meta_desc.get("content"))
        og_desc = soup.find("meta", property="og:description")
        if isinstance(og_desc, Tag) and og_desc.get("content"):
            return str(og_desc.get("content"))
        return "" 
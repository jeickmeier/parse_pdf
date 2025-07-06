import asyncio
from types import SimpleNamespace

import pytest
from PIL import Image

from doc_parser.parsers.pdf.extractors import VisionExtractor


@pytest.fixture()
def blank_image():  # noqa: D401
    return Image.new("RGB", (10, 10), color="white")


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------


def test_get_default_prompt(monkeypatch):
    # Monkeypatch PromptRegistry to supply a known template
    from doc_parser.prompts.base import PromptTemplate, PromptRegistry

    tmpl = PromptTemplate("PROMPT")
    monkeypatch.setattr(PromptRegistry, "_templates", {"pdf_extraction": tmpl}, raising=False)

    extractor = VisionExtractor()
    assert extractor.get_default_prompt() == "PROMPT"


def test_get_prompt_resolution(monkeypatch):
    from doc_parser.prompts.base import PromptTemplate

    extractor = VisionExtractor()

    # Case 1: None -> default
    monkeypatch.setattr(extractor, "get_default_prompt", lambda: "DEFAULT")
    assert extractor._get_prompt(None) == "DEFAULT"  # noqa: SLF001

    # Case 2: PromptTemplate instance
    pt = PromptTemplate("HELLO {{x}}", {"x": "X"})
    assert extractor._get_prompt(pt) == "HELLO X"

    # Case 3: string treated as literal prompt
    assert extractor._get_prompt("LITERAL") == "LITERAL"


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_extract_single(monkeypatch, blank_image):
    extractor = VisionExtractor()

    async def fake_call(prompt: str, base64_str: str):  # noqa: D401, ARG002
        assert prompt == "PROMPT"
        return "RESULT"

    monkeypatch.setattr(extractor, "_call_vision_api", fake_call, raising=True)
    monkeypatch.setattr(extractor, "get_default_prompt", lambda: "PROMPT")

    output = await extractor.extract(blank_image)
    assert output == "RESULT"


@pytest.mark.asyncio
async def test_extract_batch(monkeypatch, blank_image):
    extractor = VisionExtractor()

    async def fake_single(self, img, prompt_template=None):  # noqa: ARG002, D401
        return "PAGE"

    monkeypatch.setattr(extractor, "_extract_single", fake_single, raising=True)

    images = [blank_image, blank_image]
    combined = await extractor.extract(images)
    # should join pages with double newline
    assert combined == "PAGE\n\nPAGE"


# ---------------------------------------------------------------------------
# _call_vision_api – patch Runner.run to avoid network
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_call_vision_api(monkeypatch):
    extractor = VisionExtractor()

    # Create dummy result object returned by Runner.run
    dummy = SimpleNamespace(final_output="VISION")

    async def fake_run(agent, messages):  # noqa: D401, ARG002
        return dummy

    monkeypatch.setattr("doc_parser.parsers.pdf.extractors.Runner.run", fake_run, raising=True)

    out = await extractor._call_vision_api("PROMPT", "base64")
    assert out == "VISION" 
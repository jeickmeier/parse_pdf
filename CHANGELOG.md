# Changelog

## [Unreleased]

### Breaking

- Removed all synchronous "shim" helpers and convenience wrappers:
  - `BaseParser.parse_sync` has been deleted. Callers should use `asyncio.run(parser.parse(...))` instead.
  - CLI now internally wraps `parser.parse()` with `asyncio.run`, eliminating duplicate sync/async code paths.

### Breaking (Prompt Template Refactor)

- **Jinja2 dependency removed** – The legacy `doc_parser.prompts.base.PromptTemplate` and
  accompanying `PromptRegistry` have been **deleted**.  All prompt templates now use the
  Pydantic-powered `doc_parser.prompts.PromptTemplate` model that renders Markdown via
  standard Python `str.format` placeholders.  No runtime Jinja2 dependency remains.
- Public API changes:
  - `PromptRegistry` no longer exists – pass the *rendered* prompt text or a `PromptTemplate`
    instance directly.
  - Import path is now `from doc_parser.prompts import PromptTemplate`.
- Project dependency list no longer includes **Jinja2** – run `uv pip sync` (or
  `pip install -U -r requirements.txt`) to clean up your environment.

### Added / Changed

- Documentation, README examples, and internal docstrings updated to reflect async-first API.
- Minimum supported Python version remains `>=3.12` (already enforced in `pyproject.toml`).
- Unified prompt system; templates bundled in `doc_parser/prompts/templates` are now Markdown-only.
- Documentation and examples updated accordingly.
- **Fail-fast error-handling policy**: parsers now catch only *expected* errors declared in `doc_parser.core.error_policy` (IOError, ValueError, `aiohttp.ClientError`, PDF2Image exceptions, etc.).   Unexpected exceptions propagate to callers.
- Debug-level logging on handled errors via the new `doc_parser.utils.logging_config` module (auto-configured; toggle with `DOC_PARSER_DEBUG=1`).
- Unit tests (`tests/core/test_error_handling_policy.py`) validate the behaviour.

### Migration Guide

1. Replace any call sites of `parse_sync`:

```python
# Before
result = parser.parse_sync(path)

# After
import asyncio
result = asyncio.run(parser.parse(path))
```

2. Ensure your environment is running Python 3.11+ (preferably 3.12 matching project targets).

No other public API changes were made.

### Migration Steps

1. Replace `from doc_parser.prompts.base import PromptTemplate, PromptRegistry` with
   `from doc_parser.prompts import PromptTemplate`.
2. Convert double-brace placeholders `{{var}}` in your templates to single braces `{var}`.
3. If you relied on `PromptRegistry`, remove the registration call and instead store your
   template on disk and load it with `PromptTemplate.from_file()` or construct the prompt
   string inline.
4. Uninstall Jinja2 if it was brought in via this project: `pip uninstall jinja2` (optional). 
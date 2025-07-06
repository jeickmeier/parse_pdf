# Changelog

## [Unreleased]

### Breaking

- Removed all synchronous "shim" helpers and convenience wrappers:
  - `BaseParser.parse_sync` has been deleted. Callers should use `asyncio.run(parser.parse(...))` instead.
  - CLI now internally wraps `parser.parse()` with `asyncio.run`, eliminating duplicate sync/async code paths.

### Added / Changed

- Documentation, README examples, and internal docstrings updated to reflect async-first API.
- Minimum supported Python version remains `>=3.12` (already enforced in `pyproject.toml`).

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
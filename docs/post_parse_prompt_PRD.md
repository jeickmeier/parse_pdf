# Product Requirements Document (PRD)

## "Post-Parse Prompting" – v0.1

### 1. Problem / Opportunity
Today `doc_parser` ends after generating primary output (Markdown/JSON/HTML). Many downstream use-cases (summaries, flash-cards, domain-specific extraction) still require a second LLM call on that primary output. Users must currently script this themselves → duplicated boiler-plate, no caching, no CLI flag, no consistent error handling.

### 2. Goals
A. Give every parser the **option** to pipe its primary Markdown result into OpenAI (or future LLMs) with a *secondary prompt*.
B. Return the "secondary output" to the caller alongside the original parse result.
C. Allow secondary output to be:
   * Free-form text, **or**
   * Validated structured data via a user-supplied Pydantic model (JSON mode).
D. Integrate seamlessly with existing async flow, caching, and CLI.

### 3. Non-Goals
* Building an in-house LLM.
* Complex prompt-engineering UI.
* Automatic schema discovery from primary content.

### 4. User Stories
1. **CLI** – As a CLI user I can add `--post-prompt "<prompt text>"` and receive a second section printed below the primary Markdown.
2. **SDK** – As a developer I can pass `post_prompt` or `post_prompt_template` to `parser.parse_with_cache()` and get an extra field `post_content` in `ParseResult`.
3. **Schema Mode** – I can additionally supply `response_model=MySchema` (Pydantic BaseModel) and receive `post_content` as an **instance** of that model (validation errors bubble up).
4. **Caching Control** – I can disable/enable caching independently for the second call.

### 5. Functional Requirements
* **FR-1**  Extend `ParserConfig`
  * `post_prompt: Optional[str] = None`
  * `response_model: Optional[str] = None` (import path)
  * `post_use_cache: bool = True`
* **FR-2**  Extend `ParseResult`
  ```python
  post_content: Any = None
  post_errors: List[str] = field(default_factory=list)
  ```
* **FR-3**  New util `LLMPostProcessor`
* **FR-4**  Integrate into each parser after primary extraction.
* **FR-5**  CLI flags: `--post-prompt`, `--post-prompt-template`, `--response-model`, `--no-post-cache`.
* **FR-6**  Errors stored in `post_errors`; do not abort primary parse unless `--strict-post` flag.
* **FR-7**  Docs + examples.

### 6. Non-Functional Requirements
* One additional LLM call max.
* Respect rate-limiter & retries.
* Backwards compatible when `post_prompt` not set.
* Unit-tests ≥90 % coverage for new logic.

### 7. API Design Sketch
```python
result = await parser.parse_with_cache(
    file_path,
    post_prompt="Summarize in 5 bullet points",
    response_model="myproj.models.BulletSummary"
)
print(result.post_content)
```

### 8. Data / Caching
Key: `SHA256(primary_md + prompt + response_model_path + model_name)` → stored via `CacheManager`.

### 9. Security & Privacy
* Warn users that primary content is sent to OpenAI.
* `--no-post` flag for privacy-sensitive contexts.

### 10. Testing Plan
* Unit tests for `LLMPostProcessor` (mocked client).
* Integration tests through CLI.
* Cache behaviour tests.

### 11. Roll-out / Migration
* Version bump to `0.2.0`.
* Release notes emphasise opt-in nature.

### 12. Open Questions
1. Support non-OpenAI providers now or later?
2. Streaming of post-prompt output?
3. Nested post-prompts (chains)?

### 13. Timeline & Milestones
* Week 1 – API & config changes, unit tests.
* Week 2 – Integrate into parsers, update CLI, docs.
* Week 3 – Comprehensive tests, examples, release prep.

### 14. Success Metrics
* <5 % overhead when post-prompt disabled.
* ≤1 % parsing regressions.
* ≥80 % of beta users report reduced boiler-plate. 
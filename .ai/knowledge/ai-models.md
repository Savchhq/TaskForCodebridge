# AI Models & Provider Guidelines

## Primary Model
* **Model**: Google Gemini Flash (e.g. `gemini-2.5-flash` or `gemini-1.5-flash` via `google-genai` SDK).
* **Configuration**:
  * Set `temperature: 0.0` or low temperature for deterministic structured extraction.
  * Use structured output schemas (JSON Schema / Pydantic).
  * Enforce source reference extraction (`page_number`, `source_snippet`).

## Provider Architecture
* Defined in `backend/app/services/ai/base.py`.
* Any provider must implement:
  * `extract_offer(text_by_page: list[dict]) -> RawOffer`
  * `match_items(original_items, revised_items) -> list[MatchItemDecision]`
* Implementations:
  * `GeminiFlashProvider`: Live API calls.
  * `MockAIProvider`: Static fixtures for tests and offline development.

## Prompt Guidelines
1. Do not ask LLM to perform mathematical additions or multiplications.
2. Instruct the model to extract literal raw numbers and strings from the text.
3. Instruct the model to cite the exact substring from the page where each value was found.
4. When matching items, instruct the model to provide a brief semantic explanation and a confidence score (0.0 to 1.0).

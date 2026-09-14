# T-004: AI Extraction & Semantic Matching Pipeline

* **Status**: DONE
* **Responsible Agent**: AI Agent
* **Dependencies**: T-002, T-003

## Goal
Implement the LLM-powered extraction and item matching pipeline behind a clean provider interface.

## Requirements
1. `BaseAIProvider` interface defining:
   - `extract_offer_data(pages: list[PageContent]) -> OfferDocument`
   - `match_line_items(original: list[LineItem], revised: list[LineItem]) -> list[ItemMatch]`
2. `GeminiFlashProvider` implementation using the official Gemini SDK.
3. `MockAIProvider` for test execution without network calls or API keys.
4. Prompts:
   - Structured JSON prompt for commercial data extraction with source citations.
   - Semantic item matching prompt: detects renamed products, assigns confidence score (0.0 - 1.0), provides short rationale.

## Acceptance Criteria
- [x] `BaseAIProvider`, `GeminiFlashProvider`, and `MockAIProvider` in `backend/app/services/ai/`.
- [x] Tests in `backend/tests/test_ai_provider.py` using `MockAIProvider` pass deterministically.

## Completed Work
- Defined `BaseAIProvider` in `backend/app/services/ai/base.py` with `TokenUsage` accounting and pricing calculation for Gemini Flash.
- Implemented `GeminiFlashProvider` in `backend/app/services/ai/gemini_provider.py` utilizing the official `google-genai` SDK with strict JSON schema outputs and automatic source citation verification.
- Implemented deterministic `MockAIProvider` in `backend/app/services/ai/mock_provider.py` supporting `ground_truth.json` benchmarks (renamed, added, removed, reordered, ambiguous items) and heuristic fallback.
- Authored structured system and task prompts in `backend/app/services/ai/prompts.py` enforcing arithmetic integrity (anti-calculation instruction), verbatim source citation, and confidence classification (`CONFIRMED` >= 0.8, `UNCERTAIN` < 0.8).
- Implemented factory `get_ai_provider` in `backend/app/services/ai/__init__.py`.
- Created 20 comprehensive unit tests in `backend/tests/test_ai_provider.py` (76 total backend tests passing).

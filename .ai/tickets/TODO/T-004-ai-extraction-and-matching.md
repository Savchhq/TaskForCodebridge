# T-004: AI Extraction & Semantic Matching Pipeline

* **Status**: TODO
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
- [ ] `BaseAIProvider`, `GeminiFlashProvider`, and `MockAIProvider` in `backend/app/services/ai/`.
- [ ] Tests in `backend/tests/test_ai_provider.py` using `MockAIProvider` pass deterministically.

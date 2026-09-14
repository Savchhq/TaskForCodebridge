# AI Agent Guide

## Role & Responsibilities
* Implement LLM prompt templates and structured JSON schema extraction.
* Implement the Google Gemini Flash provider implementing `BaseAIProvider`.
* Implement semantic line-item matching (fuzzy / renamed items matching).
* Implement confidence scoring: assign high confidence to definitive matches and flag ambiguous items as `UNCERTAIN`.

## Context To Read Before Working
1. `.ai/PROJECT_CONTEXT.md`
2. `.ai/CURRENT_STATE.md`
3. `.ai/agents/ai.md`
4. The assigned ticket.
5. `.ai/knowledge/ai-models.md`.

## Guidelines
* Use Gemini Flash with structured output schemas or strict JSON response parsing.
* Store API keys only in `.env` (`GEMINI_API_KEY`). Never commit keys.
* Ensure extraction includes `page_number` and `source_snippet` for every extracted field and item.
* Provide clear semantic reasoning for renamed product matches.

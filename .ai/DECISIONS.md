# Architectural & Product Decisions (ADR)

## ADR-001: Technology Stack
* **Date**: 2026-09-14
* **Decision**: 
  * Backend: Python 3.10+, FastAPI, Pydantic v2.
  * PDF Parsing: `pdfplumber` (native page segmentation, text & layout retention).
  * Frontend: React 18, Vite, Tailwind CSS.
  * Storage: Ephemeral / in-memory. No database, no user authentication.
* **Rationale**: Fast development velocity, strict type validation, minimal overhead, perfect for an 8-hour MVP.

## ADR-002: AI Provider & Interface
* **Date**: 2026-09-14
* **Decision**: 
  * Primary LLM: Google Gemini Flash.
  * Integration: Abstracted behind a `BaseAIProvider` interface.
  * Secrets: API key read strictly from `.env` via `GEMINI_API_KEY`. No hardcoded credentials.
* **Rationale**: Fast inference, cost-efficient, high quality structured outputs, with swappable design for other models (OpenAI, Anthropic, or mock test providers).

## ADR-003: Source Reference Granularity
* **Date**: 2026-09-14
* **Decision**: 
  * Every extracted field and detected change must reference `page_number: int` and `source_snippet: str` (verbatim or near-verbatim text from the PDF).
* **Rationale**: Satisfies the traceability requirement without overengineering coordinate-based PDF overlay rendering in an 8-hour window.

## ADR-004: Boundary Between AI and Deterministic Code
* **Date**: 2026-09-14
* **Decision**:
  * **AI Scope**: Semantic understanding, field extraction, fuzzy item matching (renamed products), change classification rationale.
  * **Deterministic Python Scope**: Arithmetic recalculation (`qty * unit_price`, sum of items vs. grand total), discrepancy detection.
  * **Integrity Rule**: Never allow AI to silently overwrite or "fix" bad math in the source document. Raw values are preserved and flagged as math discrepancies.
* **Rationale**: Eliminates arithmetic hallucination and guarantees auditing fidelity.

## ADR-005: Domain Data Contracts & Type Mirroring
* **Date**: 2026-09-14
* **Decision**:
  * Implement unified domain contracts in `backend/app/models/schemas.py` using Pydantic v2.
  * Explicitly mirror schemas as TypeScript interfaces and string enums in `frontend/src/types/index.ts`.
  * Support `extra="ignore"` for domain entities (`LineItem`, `OfferDocument`, `ComparisonReport`) and `extra="allow"` for `ComparisonSummary` to facilitate extensibility.
  * Standardize all substantive diff operations around `ChangeType` and `ConfidenceLevel` string enums to ensure clean JSON serialization and interoperability.
* **Rationale**: Strong type safety across the Python backend and React frontend prevents contract drift, simplifies frontend rendering of diffs and audits, and provides early validation for AI extraction outputs.

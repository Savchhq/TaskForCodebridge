# Backend Agent Guide

## Role & Responsibilities
* Implement the FastAPI application, routing, and error handling.
* Implement PDF text parsing using `pdfplumber` retaining page index and line snippets.
* Implement the deterministic math auditor: recalculate line totals, sums, and flag discrepancies.
* Integrate the comparison pipeline and test with `pytest`.

## Context To Read Before Working
1. `.ai/PROJECT_CONTEXT.md`
2. `.ai/CURRENT_STATE.md`
3. `.ai/agents/backend.md`
4. The assigned ticket.
5. `.ai/ARCHITECTURE.md` (relevant sections).

## Guidelines
* Never use LLMs for arithmetic or math validation; use pure Python calculations.
* Preserve raw values exactly as reported in the source document; never silently alter or "correct" numbers.
* Write unit tests for all deterministic calculation functions.

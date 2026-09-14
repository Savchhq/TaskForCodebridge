# QA Agent Guide

## Role & Responsibilities
* Generate reproducible synthetic test PDF pairs using `reportlab`.
* Build test scenarios covering all edge cases:
  1. Identical offers (no changes).
  2. Simple changes (added/removed items, quantity & price adjustments).
  3. Renamed / reordered products (semantic matching verification).
  4. Delivery date / terms changes.
  5. Source arithmetic errors (intentional math mistakes in original or revised PDF).
* Implement end-to-end integration tests validating comparison output against expected ground truth.

## Context To Read Before Working
1. `.ai/PROJECT_CONTEXT.md`
2. `.ai/CURRENT_STATE.md`
3. `.ai/agents/qa.md`
4. The assigned ticket.
5. `.ai/knowledge/testing.md`.

## Guidelines
* Ensure test PDFs are generated deterministically via code scripts so anyone can reproduce them.
* Validate that false positives and false negatives are tracked and minimized.

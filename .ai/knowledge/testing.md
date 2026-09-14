# Testing Specification & Reproducible Test Set

## Required Test Scenarios (from Brief)

### Scenario 1: Primary Comprehensive Test Pair (`offer_v1.pdf` vs `offer_v2_substantive.pdf`)
* **Input Specs**: Text-based PDFs, 1 currency (e.g. USD), ~5-8 items, 1-2 pages.
* **Ground Truth Changes to Assert**:
  1. **Renamed Item**: e.g., "Cloud Server Hosting Tier A" -> "Tier-A Cloud Compute Instance" (matched semantically).
  2. **Reordered Rows**: Items displayed in a completely different row order.
  3. **Quantity Change**: e.g., 5 units -> 8 units.
  4. **Unit Price Change**: e.g., $150.00 -> $175.00.
  5. **Removed Item**: 1 item from original completely omitted.
  6. **Added Item**: 1 new item introduced in revised offer.
  7. **Delivery Date Change**: e.g., 2026-10-01 -> 2026-11-15.
  8. **Incorrect Total (Arithmetic Error)**:
     - Deliberate printed mistake in original or revised offer (e.g. line items sum to $4,500, but printed subtotal says $4,800).
     - Auditor must report arithmetic discrepancy without replacing the printed value.
  9. **Formatting Variations**: Different fonts, table border styles, and spacing. Auditor/Diff must ignore these.
  10. **Dual Source Verification**: Both original and revised page and snippet must be verified for all modified items.

### Scenario 2: Formatting-Only Variant (`offer_v1.pdf` vs `offer_v1_reformatted.pdf`)
* **Input Specs**: The exact same commercial terms as `offer_v1.pdf`, but generated with different font sizes, line wrapping, alternating background colors, and margin spacing.
* **Ground Truth**: **0 substantive changes**.
* **Assertion**: `len(changes) == 0`.

### Scenario 3: Ambiguity / Clarification Pair (`offer_v1.pdf` vs `offer_v2_ambiguous.pdf`)
* **Input Specs**: Revised document has an item with completely ambiguous or conflicting specs (e.g. "General Consulting Services" with no code or details vs original having "Frontend Dev" and "Backend Dev").
* **Ground Truth**: Confidence level must be marked as `UNCERTAIN` and flag that clarification is needed, rather than blindly confirming a false match.

## Automated Verification Script (`test_fixtures/run_acceptance_tests.py`)
* Sends each test pair to `/api/compare`.
* Evaluates:
  * Missed changes (false negatives).
  * False changes (false positives).
  * Presence of dual source references (`original_source_ref` AND `revised_source_ref`).
  * Measured latency (`processing_time_ms`).
  * Calculated token cost (`estimated_cost_usd`).

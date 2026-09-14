# T-008: Reproducible Test PDF Generator & E2E Acceptance Verification

* **Status**: DONE
* **Responsible Agent**: QA Agent
* **Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006

## Goal
Provide a deterministic script that generates commercial offer PDF test pairs and runs automated end-to-end acceptance tests verifying all business requirements.

## Deliverables & Results
1. **Deterministic Test PDF Suite (`test_fixtures/generate_test_pdfs.py`)**:
   - `test_fixtures/samples/offer_v1.pdf`: Baseline IT/Cloud proposal (6 items, 1 currency USD, 1 page, 0 math errors).
   - `test_fixtures/samples/offer_v2_substantive.pdf`: Revised offer with 1 renamed position, reordered rows, 1 qty change, 1 price change, 1 removed item, 1 added item, 1 delivery date change, and 1 deliberate math error ($1,000 * 1 != $1,200).
   - `test_fixtures/samples/offer_v1_reformatted.pdf`: Radical styling/font shift of baseline proposal resulting in EXACTLY 0 commercial changes.
   - `test_fixtures/samples/offer_v2_ambiguous.pdf`: Unclear item description without SKU requiring `UNCERTAIN` confidence classification.
   - `test_fixtures/samples/ground_truth.json`: Machine-readable benchmarks and expected verification criteria.

2. **Automated Acceptance Runner (`test_fixtures/run_acceptance_tests.py`)**:
   - Executes all 3 benchmark scenarios through FastAPI `TestClient(app)` against `/api/compare`.
   - Asserts:
     * 7 substantive changes detected on Pair 1 (renamed, quantity, unit price, removed, added, delivery date, grand total).
     * 1 deliberate arithmetic discrepancy flagged in revised audit (`Line item: 24/7 DevOps Support & SLA Package`).
     * Strict dual source reference attribution for all changes (verbatim snippet + page citation).
     * Exact 0 changes on formatting-only revision (0 false positives).
     * Ambiguous item flagged with `confidence=UNCERTAIN` requiring clarification.
   - Measures latency, token consumption, and cost per document pair.

3. **Acceptance Report (`test_fixtures/ACCEPTANCE_REPORT.md`)**:
   - Published report with executive summary, latency/cost scorecard, and granular change verification tables suitable for Delivery Notes.

## Acceptance Criteria
- [x] Test generation script runs and outputs valid PDFs to `test_fixtures/samples/`.
- [x] Acceptance verification script confirms all edge cases pass with 100% accuracy.
- [x] Dual source references verified for all detected modifications.
- [x] Formatting exemption confirmed (0 false positives).
- [x] Latency, token metrics, and cost per pair reported.

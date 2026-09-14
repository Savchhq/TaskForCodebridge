# T-008: Reproducible Test PDF Generator & E2E Verification

* **Status**: TODO
* **Responsible Agent**: QA Agent
* **Dependencies**: T-006, T-007

## Goal
Provide a deterministic script that generates commercial offer PDF test pairs and runs end-to-end acceptance tests.

## Requirements
1. Generator Script (`test_fixtures/generate_test_pdfs.py`):
   - Uses `reportlab` to generate professional-looking, text-based PDFs.
   - Generates at least 4 test pairs:
     - Pair 1: Clean changes (1 added, 1 removed, 1 qty change, 1 price change, updated delivery date).
     - Pair 2: Renamed items & reordered lines (testing semantic match).
     - Pair 3: Source arithmetic error (deliberate calculation mistake in original document).
     - Pair 4: Edge case (multi-page document, currency changes, discounts).
2. Automated Test Runner (`test_fixtures/run_acceptance_tests.py`):
   - Sends test pairs to backend `/api/compare`.
   - Asserts expected detected changes and arithmetic warnings match ground truth.

## Acceptance Criteria
- [ ] Test generation script runs and outputs valid PDFs to `test_fixtures/samples/`.
- [ ] Acceptance verification script confirms all edge cases pass.

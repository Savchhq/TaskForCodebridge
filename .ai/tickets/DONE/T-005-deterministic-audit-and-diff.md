# T-005: Deterministic Math Validation & Diff Classifier

* **Status**: DONE
* **Responsible Agent**: Backend Agent
* **Dependencies**: T-002, T-004

## Goal
Implement pure-code deterministic arithmetic auditing and substantive change classification logic.

## Requirements
1. **Math Auditor (`backend/app/services/auditor.py`)**:
   - For each line item: verify `quantity * unit_price == total_price` (with float rounding tolerance e.g. 0.01).
   - For totals: verify `sum(item_totals) == subtotal` and `subtotal + tax/fees - discounts == grand_total`.
   - Report any discrepancy as `MathDiscrepancy(location, expected, actual, message)`.
   - Never alter source numbers.
2. **Diff Classifier (`backend/app/services/diff_engine.py`)**:
   - Takes matched items from AI provider.
   - Categorizes changes:
     - Missing in revised: `REMOVED`
     - Missing in original: `ADDED`
     - Renamed items: `RENAMED` (flag as UNCERTAIN if match confidence < 0.8)
     - Quantity diff: `QUANTITY_CHANGED`
     - Unit price diff: `UNIT_PRICE_CHANGED`
     - Delivery date change: `DELIVERY_DATE_CHANGED`
   - Filter out formatting-only / trivial changes (ignore whitespace and casing).

## Acceptance Criteria
- [x] Unit tests for math auditor with deliberate errors pass.
- [x] Unit tests for diff classifier covering all change types pass.

## Deliverables & Verification
- `backend/app/services/auditor.py`: Pure Python arithmetic verification for items, subtotals, and grand totals with strict immutability.
- `backend/app/services/diff_engine.py`: Commercial substantive change synthesizer with dual source references, formatting exemption (0 changes for formatting variants), and summary metrics calculation.
- `backend/tests/test_auditor.py`: 12 unit tests verifying calculation error detection, immutability, and edge cases.
- `backend/tests/test_diff_engine.py`: 6 unit tests covering ADDED, REMOVED, RENAMED (CONFIRMED & UNCERTAIN), QUANTITY_CHANGED, UNIT_PRICE_CHANGED, TOTAL_CHANGED, DELIVERY_DATE_CHANGED, formatting exemption, and summary metrics.

# T-007: Frontend Comparison Dashboard UI

* **Status**: TODO
* **Responsible Agent**: Frontend Agent
* **Dependencies**: T-002, T-006

## Goal
Build a clean, responsive comparison dashboard in React + Tailwind.

## Requirements
1. **Upload Section**:
   - Two file upload dropzones ("Original Commercial Offer" & "Revised Commercial Offer").
   - "Compare Offers" trigger button with loading spinner / progress state.
2. **Summary Banner**:
   - Total items original vs revised.
   - Grand total original vs revised & net difference.
   - Delivery date changes.
3. **Math Discrepancy Alerts**:
   - Clear warning card if source PDF contained arithmetic errors.
4. **Changes Table**:
   - Filter by change type (All, Added, Removed, Modified, Renamed, Price Changed).
   - Badge for `CONFIRMED` vs `UNCERTAIN` (amber warning badge).
   - Expandable / popover button showing `Source Reference`: Page number and verbatim quote.

## Acceptance Criteria
- [ ] Responsive layout with Tailwind CSS.
- [ ] End-to-end integration with `POST /api/compare`.
- [ ] Clear visual distinction between confirmed changes and uncertain matches.

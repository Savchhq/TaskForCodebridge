# T-007: Frontend Comparison Dashboard UI

* **Status**: DONE
* **Responsible Agent**: Frontend Agent
* **Dependencies**: T-002, T-006

## Goal
Build a clean, responsive comparison dashboard in React + Tailwind.

## Requirements
1. **Upload Section**:
   - Two file upload dropzones ("Original Commercial Offer" & "Revised Commercial Offer").
   - "Compare Offers" trigger button with loading spinner / progress state.
   - Provider switcher: Auto (Gemini Flash / Mock), Demo / Mock, and Gemini Flash.
   - One-click presets for test scenarios (Scenario 1, Scenario 2, Scenario 3).
2. **Summary Banner**:
   - Total items original vs revised.
   - Grand total original vs revised & net difference.
   - Delivery date changes.
   - Performance (processing_time_ms) & token cost (estimated_cost_usd).
3. **Math Discrepancy Alerts**:
   - Clear warning card if source PDF contained arithmetic errors (printed vs calculated).
4. **Changes Table**:
   - Filter by change type (All, Added, Removed, Modified, Renamed, Quantity, Price, Delivery Date).
   - Badge for `CONFIRMED` (green) vs `UNCERTAIN` (amber warning badge).
   - Modal / Popover showing dual `Source Reference`: Page number and verbatim quote for both original and revised documents.

## Acceptance Criteria
- [x] Responsive layout with Tailwind CSS.
- [x] End-to-end integration with `POST /api/compare`.
- [x] Clear visual distinction between confirmed changes and uncertain matches.
- [x] Clean production build with `npm run build` (0 TypeScript / lint errors).

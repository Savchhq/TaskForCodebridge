# T-002: Data Contracts & Domain Schemas

* **Status**: DONE
* **Responsible Agent**: Architect Agent
* **Dependencies**: T-001

## Goal
Define type-safe Pydantic models for extracted PDF data, deterministic calculations, semantic matching, and comparison diff reports.

## Requirements
1. `SourceReference`: `page_number: int`, `snippet: str`
2. `LineItem`: `item_id: str | None`, `name: str`, `description: str | None`, `quantity: float | None`, `unit: str | None`, `unit_price: float | None`, `total_price: float | None`, `source_ref: SourceReference | None`
3. `OfferDocument`: `vendor_name: str | None`, `client_name: str | None`, `offer_id: str | None`, `offer_date: str | None`, `delivery_date: str | None`, `currency: str | None`, `items: list[LineItem]`, `subtotal: float | None`, `tax: float | None`, `grand_total: float | None`
4. `MathDiscrepancy`: `location: str`, `expected_value: float`, `actual_value: float`, `message: str`
5. `AuditReport`: `document_name: str`, `is_valid: bool`, `discrepancies: list[MathDiscrepancy]`
6. `ChangeType`: `ADDED`, `REMOVED`, `RENAMED`, `QUANTITY_CHANGED`, `UNIT_PRICE_CHANGED`, `TOTAL_CHANGED`, `DELIVERY_DATE_CHANGED`
7. `ConfidenceLevel`: `CONFIRMED`, `UNCERTAIN`
8. `DetectedChange`: `change_type: ChangeType`, `item_name_original: str | None`, `item_name_revised: str | None`, `original_value: Any`, `revised_value: Any`, `confidence: ConfidenceLevel`, `explanation: str`, `original_source_ref: SourceReference | None`, `revised_source_ref: SourceReference | None`
9. `ComparisonReport`: `original_audit: AuditReport`, `revised_audit: AuditReport`, `changes: list[DetectedChange]`, `summary: dict`

## Acceptance Criteria
- [x] Models defined in `backend/app/models/schemas.py`.
- [x] Schema validation unit tests passing in `backend/tests/test_schemas.py`.
- [x] TypeScript type declarations generated or mirrored in `frontend/src/types/index.ts`.

## Deliverables & Verification
- `backend/app/models/schemas.py` & `backend/app/models/__init__.py`: Full Pydantic v2 schemas.
- `backend/tests/test_schemas.py`: 20 unit tests covering constraints, validations, enums, serialization. All passed (21 total backend tests pass).
- `frontend/src/types/index.ts`: Full mirrored TypeScript definitions; `npm run build` succeeds cleanly.


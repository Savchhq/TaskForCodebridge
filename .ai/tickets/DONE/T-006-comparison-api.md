# T-006: Comparison API Endpoint

* **Status**: DONE
* **Responsible Agent**: Backend Agent
* **Dependencies**: T-003, T-004, T-005

## Goal
Expose a single end-to-end API endpoint that receives two PDF files and returns the full comparison analysis.

## Requirements
1. Endpoint: `POST /api/compare`
   - Accepts `multipart/form-data`: `original_file` (UploadFile) and `revised_file` (UploadFile).
   - Validates file formats (must be PDF).
2. Pipeline orchestration:
   - Extract raw pages from both PDFs.
   - Run AI extraction for both documents.
   - Run deterministic math audit on both documents.
   - Run semantic matching across line items.
   - Run diff classifier to generate substantive changes.
   - Assemble `ComparisonReport` response.
3. CORS middleware configured to allow frontend development requests.

## Acceptance Criteria
- [x] `POST /api/compare` handles two PDF uploads and returns 200 OK with `ComparisonReport`.
- [x] Integration test in `backend/tests/test_api.py`.

## Deliverables & Verification
- `backend/app/api/endpoints.py`: `POST /api/compare` endpoint supporting multipart PDF upload, provider selection (`auto`, `gemini`, `mock`), file validation, error handling, and performance tracking.
- `backend/app/api/__init__.py`: Router export.
- `backend/app/main.py`: Mounted `/api` router alongside CORS and health check.
- `backend/tests/test_api.py`: 4 integration tests verifying successful 200 OK comparison, rejection of non-PDF files, rejection of corrupted PDFs, and validation of provider query parameter. All 86 backend tests pass.

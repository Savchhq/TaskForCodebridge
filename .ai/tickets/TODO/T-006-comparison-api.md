# T-006: Comparison API Endpoint

* **Status**: TODO
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
- [ ] `POST /api/compare` handles two PDF uploads and returns 200 OK with `ComparisonReport`.
- [ ] Integration test in `backend/tests/test_api.py`.

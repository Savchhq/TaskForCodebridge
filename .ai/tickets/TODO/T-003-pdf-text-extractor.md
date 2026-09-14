# T-003: PDF Text & Layout Extraction Engine

* **Status**: TODO
* **Responsible Agent**: Backend Agent
* **Dependencies**: T-001, T-002

## Goal
Implement a robust, deterministic PDF text extraction service that parses text-based PDFs (up to 3 pages) and preserves page numbers and text blocks to guarantee dual source reference attribution.

## Requirements
1. Use `pdfplumber` for page-by-page text extraction.
2. In `backend/app/services/pdf_extractor.py`:
   - `extract_pdf_pages(file_content: bytes | BinaryIO) -> list[PageContent]`
     - Each page must contain `page_number` (1-indexed), `raw_text` (normalized text), and `lines` (list of non-empty text lines).
   - `find_source_snippet(pages: list[PageContent], search_term: str) -> SourceReference | None`
     - Searches for `search_term` (or matching phrase) across pages and returns a `SourceReference` containing the exact `page_number` and the verbatim context snippet.
3. Handle edge cases:
   - Multi-page documents (up to 3 pages).
   - Documents with tables, headers, and footer lines.
   - Corrupted or non-PDF bytes (raise clean `ValueError("Invalid PDF file")`).
   - Empty pages (handled gracefully without crashing).
4. Unit tests in `backend/tests/test_pdf_extractor.py` verifying extraction on in-memory generated PDFs (`reportlab`) covering 1-page, 3-page, and edge-case inputs.

## Acceptance Criteria
- [ ] `extract_pdf_pages` successfully extracts text and lines with page numbers.
- [ ] `find_source_snippet` reliably locates text and builds valid `SourceReference`.
- [ ] All tests in `backend/tests/test_pdf_extractor.py` pass.

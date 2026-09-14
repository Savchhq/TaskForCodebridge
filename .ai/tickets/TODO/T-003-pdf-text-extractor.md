# T-003: PDF Text & Layout Extraction Engine

* **Status**: TODO
* **Responsible Agent**: Backend Agent
* **Dependencies**: T-001, T-002

## Goal
Implement a reliable PDF text extraction service that parses text-based PDFs and preserves page numbers and text blocks for source attribution.

## Requirements
1. Use `pdfplumber` to extract text page-by-page.
2. Return a structured representation: `list[PageContent]` where each page contains `page_number`, `raw_text`, and extracted lines/blocks.
3. Provide a helper to locate and extract a context snippet around any substring or line.
4. Graceful handling of multi-page documents and empty/corrupted PDFs.

## Acceptance Criteria
- [ ] Service implemented in `backend/app/services/pdf_extractor.py`.
- [ ] Unit tests in `backend/tests/test_pdf_extractor.py` parsing sample PDF files.

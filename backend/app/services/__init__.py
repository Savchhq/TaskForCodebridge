"""Services package for backend processing."""

from app.services.auditor import audit_line_item, audit_offer_document
from app.services.diff_engine import synthesize_comparison_report
from app.services.pdf_extractor import (
    extract_full_text,
    extract_pdf_pages,
    find_source_snippet,
)

__all__ = [
    "extract_pdf_pages",
    "find_source_snippet",
    "extract_full_text",
    "audit_line_item",
    "audit_offer_document",
    "synthesize_comparison_report",
]

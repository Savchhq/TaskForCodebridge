"""
API Endpoints for commercial offer comparison.
Provides POST /api/compare for comparing two text-based PDF offers.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.models.schemas import ComparisonReport
from app.services.ai import get_ai_provider
from app.services.diff_engine import synthesize_comparison_report
from app.services.pdf_extractor import extract_pdf_pages

logger = logging.getLogger(__name__)

router = APIRouter(tags=["comparison"])


def _is_pdf_file(file: UploadFile) -> bool:
    """Validate whether an uploaded file is a PDF based on extension or MIME type."""
    name = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()
    return name.endswith(".pdf") or "pdf" in content_type


@router.post(
    "/compare",
    response_model=ComparisonReport,
    status_code=status.HTTP_200_OK,
    summary="Compare two commercial offer PDFs",
    description=(
        "Uploads original and revised PDF offers, extracts structured data, "
        "audits arithmetic, semantically matches line items, and returns "
        "a categorized substantive change report with dual source references."
    ),
)
async def compare_offers(
    original_file: UploadFile = File(..., description="Original commercial offer PDF"),
    revised_file: UploadFile = File(..., description="Revised commercial offer PDF"),
    provider: str = Query(
        default="auto",
        description="AI provider to use for extraction ('auto', 'gemini', 'mock')",
    ),
) -> ComparisonReport:
    """
    Handle comparison of two commercial offers in PDF format.
    """
    # 1. Validate file types
    if not _is_pdf_file(original_file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format for original_file ('{original_file.filename}'). Only PDF files are accepted.",
        )

    if not _is_pdf_file(revised_file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format for revised_file ('{revised_file.filename}'). Only PDF files are accepted.",
        )

    # 2. Read uploaded file contents
    try:
        original_bytes = await original_file.read()
        revised_bytes = await revised_file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded files: {exc}",
        )

    # 3. Extract text and page layout
    try:
        original_pages = extract_pdf_pages(original_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse original PDF: {exc}",
        )

    try:
        revised_pages = extract_pdf_pages(revised_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse revised PDF: {exc}",
        )

    # 4. Resolve AI provider
    try:
        ai_provider = get_ai_provider(provider)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # 5. Synthesize comparison report
    try:
        report = synthesize_comparison_report(
            original_pages=original_pages,
            revised_pages=revised_pages,
            ai_provider=ai_provider,
        )
        return report
    except Exception as exc:
        logger.exception("Error during commercial offer comparison pipeline")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison pipeline error: {exc}",
        )

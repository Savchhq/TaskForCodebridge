"""
PDF text extraction engine using pdfplumber.
Handles multi-page documents (up to 3 pages), table layouts, and preserves
page numbers and lines for dual source reference attribution.
"""

from __future__ import annotations

import io
import re
from typing import BinaryIO

import pdfplumber

from app.models.schemas import PageContent, SourceReference


def extract_pdf_pages(file_content: bytes | BinaryIO) -> list[PageContent]:
    """
    Extract textual content page-by-page from a PDF document.

    Args:
        file_content: Raw PDF bytes or a binary file-like stream.

    Returns:
        A list of PageContent instances containing 1-indexed page_number,
        raw_text, and non-empty lines.

    Raises:
        ValueError: If file_content is empty, corrupted, or not a valid PDF file.
    """
    if file_content is None or isinstance(file_content, str):
        raise ValueError("Invalid PDF file")

    if isinstance(file_content, (bytes, bytearray)):
        if len(file_content) == 0:
            raise ValueError("Invalid PDF file")
        stream: BinaryIO = io.BytesIO(file_content)
    else:
        stream = file_content
        if hasattr(stream, "seek") and callable(stream.seek):
            try:
                stream.seek(0)
            except Exception:
                pass

    try:
        with pdfplumber.open(stream) as pdf:
            pages: list[PageContent] = []
            for idx, page in enumerate(pdf.pages, start=1):
                extracted = page.extract_text() or ""
                normalized_text = extracted.replace("\r\n", "\n").replace("\r", "\n").strip()
                lines = [
                    line.strip()
                    for line in normalized_text.split("\n")
                    if line.strip()
                ]
                pages.append(
                    PageContent(
                        page_number=idx,
                        raw_text=normalized_text,
                        lines=lines,
                    )
                )
            return pages
    except Exception as exc:
        raise ValueError("Invalid PDF file") from exc


def find_source_snippet(
    pages: list[PageContent],
    search_term: str,
) -> SourceReference | None:
    """
    Search for a verbatim citation or term across extracted pages.

    Searches across lines and page text to return the exact page number
    and surrounding text snippet for dual source verification.

    Args:
        pages: List of PageContent objects from extract_pdf_pages.
        search_term: The keyword, phrase, or line item name to locate.

    Returns:
        SourceReference with page_number and verbatim snippet, or None if not found.
    """
    if not search_term or not search_term.strip() or not pages:
        return None

    clean_term = search_term.strip()
    term_lower = clean_term.lower()
    norm_term = re.sub(r"\s+", " ", term_lower)
    words = [w for w in clean_term.split() if w]

    # Strategy 1: Exact / case-insensitive line substring match
    for page in pages:
        for line in page.lines:
            line_lower = line.lower()
            if term_lower in line_lower:
                return SourceReference(page_number=page.page_number, snippet=line.strip())

            norm_line = re.sub(r"\s+", " ", line_lower)
            if norm_term in norm_line:
                return SourceReference(page_number=page.page_number, snippet=line.strip())

    # Strategy 2: Multi-line match in raw_text (handles line wrap)
    if words:
        pattern_str = r"\s+".join(re.escape(w) for w in words)
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for page in pages:
                if not page.raw_text:
                    continue
                match = pattern.search(page.raw_text)
                if match:
                    start_pos = page.raw_text.rfind("\n", 0, match.start())
                    start_pos = 0 if start_pos == -1 else start_pos + 1
                    end_pos = page.raw_text.find("\n", match.end())
                    end_pos = len(page.raw_text) if end_pos == -1 else end_pos
                    snippet = page.raw_text[start_pos:end_pos].strip()
                    if snippet:
                        return SourceReference(
                            page_number=page.page_number,
                            snippet=snippet,
                        )
        except re.error:
            pass

    # Strategy 3: Token-subset match across lines (all significant tokens appear in line)
    sig_tokens = [tok.lower() for tok in re.findall(r"[\w$€£]+", clean_term) if len(tok) >= 2]
    if len(sig_tokens) >= 2:
        for page in pages:
            for line in page.lines:
                line_lower = line.lower()
                if all(tok in line_lower for tok in sig_tokens):
                    return SourceReference(page_number=page.page_number, snippet=line.strip())

    return None


def extract_full_text(pages: list[PageContent]) -> str:
    """
    Format all extracted pages into a single readable text representation
    with clear page demarcation headers.
    """
    sections: list[str] = []
    for page in pages:
        sections.append(f"--- Page {page.page_number} ---\n{page.raw_text}")
    return "\n\n".join(sections).strip()

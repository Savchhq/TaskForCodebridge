"""
Unit tests for PDF text and layout extraction engine.
Tests extraction, page indexing, snippet searching, error handling,
and table parsing using in-memory reportlab PDFs.
"""

import io
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from app.models.schemas import PageContent, SourceReference
from app.services.pdf_extractor import (
    extract_pdf_pages,
    find_source_snippet,
    extract_full_text,
)


def _generate_simple_pdf(page_texts: list[str]) -> bytes:
    """Helper to generate an in-memory multi-page PDF using canvas."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for text in page_texts:
        y = 750
        for line in text.split("\n"):
            c.drawString(100, y, line)
            y -= 25
        c.showPage()
    c.save()
    return buf.getvalue()


def _generate_pdf_with_empty_page() -> bytes:
    """Helper to generate a 3-page PDF where page 2 is blank."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    # Page 1
    c.drawString(100, 750, "Header Page 1: Commercial Proposal")
    c.drawString(100, 725, "Vendor: Acme Global Solutions")
    c.showPage()
    # Page 2: Empty
    c.showPage()
    # Page 3
    c.drawString(100, 750, "Total Amount: 15,000 USD")
    c.drawString(100, 725, "Signed by: John Doe")
    c.showPage()
    c.save()
    return buf.getvalue()


def _generate_commercial_offer_pdf() -> bytes:
    """Helper to generate a realistic 3-page commercial offer with tables."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Page 1: Offer Header & Metadata
    story.append(Paragraph("<b>COMMERCIAL OFFER #OFF-2026-881</b>", styles["Title"]))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Vendor: Acme Enterprise Solutions LLC", styles["Normal"]))
    story.append(Paragraph("Client: Global Logistics Partners Inc", styles["Normal"]))
    story.append(Paragraph("Offer Date: 2026-09-10", styles["Normal"]))
    story.append(Paragraph("Delivery Date: 2026-10-25", styles["Normal"]))
    story.append(Paragraph("Currency: USD", styles["Normal"]))
    story.append(Paragraph("Scope of work: Cloud infrastructure migration and setup.", styles["Normal"]))

    # Page break to Page 2
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # Page 2: Line Items Table
    story.append(Paragraph("<b>Section 2: Itemized Cost Breakdown</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))

    table_data = [
        ["Item", "Description", "Qty", "Unit Price", "Total"],
        ["Cloud Server Instance", "High-performance compute node", "4", "250.00", "1000.00"],
        ["Managed Database", "PostgreSQL clustered setup", "1", "800.00", "800.00"],
        ["DevOps Consulting", "Initial deployment and automation", "20", "100.00", "2000.00"],
    ]
    t = Table(table_data, colWidths=[130, 190, 40, 70, 70])
    story.append(t)

    # Page break to Page 3
    story.append(PageBreak())

    # Page 3: Summary & Delivery Terms
    story.append(Paragraph("<b>Section 3: Financial Summary & Terms</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Subtotal: 3800.00 USD", styles["Normal"]))
    story.append(Paragraph("Tax (20%): 760.00 USD", styles["Normal"]))
    story.append(Paragraph("Grand Total: 4560.00 USD", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph("Delivery terms: Delivery within 14 business days following contract signature.", styles["Normal"])
    )

    doc.build(story)
    return buf.getvalue()


class TestExtractPdfPages:
    """Test suite for extract_pdf_pages."""

    def test_extract_single_page_pdf(self):
        pdf_bytes = _generate_simple_pdf(["Offer #101\nVendor: Alpha Inc\nTotal: 500 USD"])
        pages = extract_pdf_pages(pdf_bytes)

        assert len(pages) == 1
        assert pages[0].page_number == 1
        assert "Offer #101" in pages[0].raw_text
        assert "Vendor: Alpha Inc" in pages[0].raw_text
        assert len(pages[0].lines) == 3
        assert pages[0].lines[0] == "Offer #101"

    def test_extract_three_page_pdf(self):
        pdf_bytes = _generate_simple_pdf([
            "Page One: Introduction\nVendor: Acme",
            "Page Two: Services\nConsulting 10 hrs",
            "Page Three: Final Total\nGrand Total: 1000 USD",
        ])
        pages = extract_pdf_pages(pdf_bytes)

        assert len(pages) == 3
        assert [p.page_number for p in pages] == [1, 2, 3]
        assert "Page One: Introduction" in pages[0].raw_text
        assert "Page Two: Services" in pages[1].raw_text
        assert "Page Three: Final Total" in pages[2].raw_text

    def test_extract_empty_page_graceful(self):
        pdf_bytes = _generate_pdf_with_empty_page()
        pages = extract_pdf_pages(pdf_bytes)

        assert len(pages) == 3
        assert pages[0].page_number == 1
        assert len(pages[0].lines) > 0

        # Blank page 2
        assert pages[1].page_number == 2
        assert pages[1].raw_text == ""
        assert pages[1].lines == []

        # Page 3
        assert pages[2].page_number == 3
        assert "Total Amount: 15,000 USD" in pages[2].raw_text

    def test_extract_commercial_offer_with_tables(self):
        pdf_bytes = _generate_commercial_offer_pdf()
        pages = extract_pdf_pages(pdf_bytes)

        assert len(pages) == 3
        # Page 1 contains vendor and offer id
        assert pages[0].page_number == 1
        assert "COMMERCIAL OFFER #OFF-2026-881" in pages[0].raw_text
        assert "Acme Enterprise Solutions LLC" in pages[0].raw_text

        # Page 2 contains table data
        assert pages[1].page_number == 2
        assert "Cloud Server Instance" in pages[1].raw_text
        assert "Managed Database" in pages[1].raw_text

        # Page 3 contains totals and terms
        assert pages[2].page_number == 3
        assert "Grand Total: 4560.00 USD" in pages[2].raw_text
        assert "Delivery terms:" in pages[2].raw_text

    def test_extract_from_binary_stream(self):
        pdf_bytes = _generate_simple_pdf(["Stream Test Content\nLine 2"])
        stream = io.BytesIO(pdf_bytes)
        pages = extract_pdf_pages(stream)

        assert len(pages) == 1
        assert "Stream Test Content" in pages[0].raw_text

    def test_extract_invalid_pdf_bytes_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid PDF file"):
            extract_pdf_pages(b"This is not a valid PDF file stream.")

    def test_extract_empty_bytes_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid PDF file"):
            extract_pdf_pages(b"")

    def test_extract_none_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid PDF file"):
            extract_pdf_pages(None)  # type: ignore

    def test_extract_string_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid PDF file"):
            extract_pdf_pages("path/to/nonexistent.pdf")  # type: ignore


class TestFindSourceSnippet:
    """Test suite for find_source_snippet."""

    @pytest.fixture
    def extracted_offer(self) -> list[PageContent]:
        pdf_bytes = _generate_commercial_offer_pdf()
        return extract_pdf_pages(pdf_bytes)

    def test_find_exact_line_on_page_one(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "Acme Enterprise Solutions LLC")
        assert ref is not None
        assert isinstance(ref, SourceReference)
        assert ref.page_number == 1
        assert "Acme Enterprise Solutions LLC" in ref.snippet

    def test_find_item_on_page_two(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "Managed Database")
        assert ref is not None
        assert ref.page_number == 2
        assert "Managed Database" in ref.snippet

    def test_find_total_on_page_three(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "Grand Total: 4560.00 USD")
        assert ref is not None
        assert ref.page_number == 3
        assert "4560.00" in ref.snippet

    def test_find_case_insensitive(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "acme enterprise solutions")
        assert ref is not None
        assert ref.page_number == 1
        assert "Acme Enterprise Solutions" in ref.snippet

    def test_find_with_irregular_whitespace(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "Cloud   Server    Instance")
        assert ref is not None
        assert ref.page_number == 2
        assert "Cloud Server Instance" in ref.snippet

    def test_find_token_subset(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "DevOps Consulting Initial deployment")
        assert ref is not None
        assert ref.page_number == 2
        assert "DevOps Consulting" in ref.snippet

    def test_find_not_found(self, extracted_offer: list[PageContent]):
        ref = find_source_snippet(extracted_offer, "NonExistentSuperWidget999")
        assert ref is None

    def test_find_empty_or_whitespace_search_term(self, extracted_offer: list[PageContent]):
        assert find_source_snippet(extracted_offer, "") is None
        assert find_source_snippet(extracted_offer, "   \t\n  ") is None

    def test_find_multiline_wrapped_text(self):
        pages = [
            PageContent(
                page_number=1,
                raw_text="Delivery conditions:\nWithin 14 calendar days\nfollowing contract signing.",
                lines=[
                    "Delivery conditions:",
                    "Within 14 calendar days",
                    "following contract signing.",
                ],
            )
        ]
        ref = find_source_snippet(pages, "Within 14 calendar days following")
        assert ref is not None
        assert ref.page_number == 1
        assert "Within 14 calendar days" in ref.snippet
        assert "following contract signing" in ref.snippet

    def test_find_with_empty_pages_list(self):
        assert find_source_snippet([], "Acme") is None


class TestExtractFullText:
    """Test suite for extract_full_text helper."""

    def test_format_multi_page_text(self):
        pages = [
            PageContent(page_number=1, raw_text="Page 1 Text", lines=["Page 1 Text"]),
            PageContent(page_number=2, raw_text="Page 2 Text", lines=["Page 2 Text"]),
        ]
        result = extract_full_text(pages)
        assert "--- Page 1 ---" in result
        assert "Page 1 Text" in result
        assert "--- Page 2 ---" in result
        assert "Page 2 Text" in result

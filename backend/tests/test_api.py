"""
Integration tests for FastAPI endpoints:
- GET /health
- POST /api/compare
"""

import io
import pytest
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _make_sample_pdf(content: str) -> bytes:
    """Helper to generate a simple in-memory PDF."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 750
    for line in content.split("\n"):
        c.drawString(100, y, line)
        y -= 25
    c.showPage()
    c.save()
    return buf.getvalue()


class TestCompareEndpoint:
    """Tests for POST /api/compare."""

    def test_compare_valid_pdfs_with_mock_provider(self, client: TestClient):
        orig_pdf = _make_sample_pdf(
            "Commercial Offer\nVendor: Acme Corp\nDelivery: 2026-10-01\n"
            "Cloud Storage: 1 unit @ $100.00 = $100.00\nTotal: $100.00"
        )
        rev_pdf = _make_sample_pdf(
            "Revised Commercial Offer\nVendor: Acme Corp\nDelivery: 2026-10-15\n"
            "Cloud Storage: 2 units @ $100.00 = $200.00\nTotal: $200.00"
        )

        response = client.post(
            "/api/compare",
            params={"provider": "mock"},
            files={
                "original_file": ("original.pdf", orig_pdf, "application/pdf"),
                "revised_file": ("revised.pdf", rev_pdf, "application/pdf"),
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "original_document" in data
        assert "revised_document" in data
        assert "original_audit" in data
        assert "revised_audit" in data
        assert "changes" in data
        assert "summary" in data
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] is not None
        assert "token_usage" in data

    def test_compare_non_pdf_file_rejected(self, client: TestClient):
        pdf_bytes = _make_sample_pdf("Valid PDF content")

        response = client.post(
            "/api/compare",
            files={
                "original_file": ("original.txt", b"plain text content", "text/plain"),
                "revised_file": ("revised.pdf", pdf_bytes, "application/pdf"),
            },
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_compare_corrupted_pdf_rejected(self, client: TestClient):
        valid_pdf = _make_sample_pdf("Valid PDF content")
        corrupted_bytes = b"Not a real PDF header or structure at all"

        response = client.post(
            "/api/compare",
            files={
                "original_file": ("original.pdf", corrupted_bytes, "application/pdf"),
                "revised_file": ("revised.pdf", valid_pdf, "application/pdf"),
            },
        )

        assert response.status_code == 400
        assert "Invalid PDF" in response.json()["detail"] or "Failed to parse" in response.json()["detail"]

    def test_compare_invalid_provider_rejected(self, client: TestClient):
        pdf_bytes = _make_sample_pdf("Valid PDF content")

        response = client.post(
            "/api/compare",
            params={"provider": "unsupported_provider_name"},
            files={
                "original_file": ("original.pdf", pdf_bytes, "application/pdf"),
                "revised_file": ("revised.pdf", pdf_bytes, "application/pdf"),
            },
        )

        assert response.status_code == 400
        assert "Unknown AI provider type" in response.json()["detail"]

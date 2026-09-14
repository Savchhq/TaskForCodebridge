"""
Unit tests for the deterministic mathematical verification engine.
Verifies line item calculations, subtotal integrity, grand total audit,
and confirms strict immutability of source document numbers.
"""

import copy
import pytest

from app.models.schemas import LineItem, OfferDocument, SourceReference
from app.services.auditor import audit_line_item, audit_offer_document


@pytest.fixture
def sample_valid_document() -> OfferDocument:
    """Fixture providing a perfectly balanced commercial offer."""
    return OfferDocument(
        vendor_name="Acme Solutions LLC",
        client_name="Beta Corp",
        offer_id="OFF-2026-001",
        currency="USD",
        items=[
            LineItem(
                name="Server Hardware",
                quantity=5.0,
                unit="units",
                unit_price=100.0,
                total_price=500.0,
                source_ref=SourceReference(page_number=1, snippet="Server Hardware: 5 x $100 = $500"),
            ),
            LineItem(
                name="Cloud Migration Service",
                quantity=2.0,
                unit="hrs",
                unit_price=250.0,
                total_price=500.0,
                source_ref=SourceReference(page_number=1, snippet="Cloud Migration Service: 2 x $250 = $500"),
            ),
        ],
        subtotal=1000.0,
        tax=200.0,
        grand_total=1200.0,
    )


class TestAuditLineItem:
    """Tests for single line item mathematical audit."""

    def test_valid_line_item(self):
        item = LineItem(name="Widget A", quantity=4.0, unit_price=25.0, total_price=100.0)
        discrepancies = audit_line_item(item)
        assert discrepancies == []

    def test_line_item_multiplication_error(self):
        # 5 * 100 should be 500, but printed total is 600
        item = LineItem(name="Widget B", quantity=5.0, unit_price=100.0, total_price=600.0)
        discrepancies = audit_line_item(item)

        assert len(discrepancies) == 1
        d = discrepancies[0]
        assert d.location == "Line item: Widget B"
        assert d.expected_value == 500.0
        assert d.actual_value == 600.0
        assert "500.00" in d.message
        assert "600.00" in d.message

    def test_line_item_partial_missing_data_does_not_crash(self):
        # Missing total_price
        item1 = LineItem(name="Item 1", quantity=5.0, unit_price=100.0, total_price=None)
        assert audit_line_item(item1) == []

        # Missing unit_price
        item2 = LineItem(name="Item 2", quantity=5.0, unit_price=None, total_price=500.0)
        assert audit_line_item(item2) == []

        # Missing quantity
        item3 = LineItem(name="Item 3", quantity=None, unit_price=100.0, total_price=500.0)
        assert audit_line_item(item3) == []

    def test_floating_point_precision_within_tolerance(self):
        # 3 * 33.33 = 99.99
        item = LineItem(name="Item Precision", quantity=3.0, unit_price=33.33, total_price=99.99)
        assert audit_line_item(item) == []


class TestAuditOfferDocument:
    """Tests for full offer document mathematical verification."""

    def test_valid_document_has_zero_discrepancies(self, sample_valid_document: OfferDocument):
        report = audit_offer_document(sample_valid_document, "Valid Offer")

        assert report.is_valid is True
        assert len(report.discrepancies) == 0
        assert report.document_name == "Valid Offer"

    def test_document_with_line_item_error(self, sample_valid_document: OfferDocument):
        # Corrupt line item calculation: 5 * 100 = 600 (printed error)
        sample_valid_document.items[0].total_price = 600.0

        report = audit_offer_document(sample_valid_document, "Corrupt Line Item")

        assert report.is_valid is False
        assert any(
            d.location == "Line item: Server Hardware" and d.expected_value == 500.0 and d.actual_value == 600.0
            for d in report.discrepancies
        )

    def test_document_with_subtotal_sum_error(self, sample_valid_document: OfferDocument):
        # Sum of items is 500 + 500 = 1000, but printed subtotal says 1150
        sample_valid_document.subtotal = 1150.0

        report = audit_offer_document(sample_valid_document, "Subtotal Error")

        assert report.is_valid is False
        assert any(
            d.location == "Subtotal" and d.expected_value == 1000.0 and d.actual_value == 1150.0
            for d in report.discrepancies
        )

    def test_document_with_grand_total_error(self, sample_valid_document: OfferDocument):
        # Subtotal (1000) + Tax (200) = 1200, but printed grand total says 1350
        sample_valid_document.grand_total = 1350.0

        report = audit_offer_document(sample_valid_document, "Grand Total Error")

        assert report.is_valid is False
        assert any(
            d.location == "Grand Total" and d.expected_value == 1200.0 and d.actual_value == 1350.0
            for d in report.discrepancies
        )

    def test_document_without_tax(self):
        doc = OfferDocument(
            items=[
                LineItem(name="Item A", quantity=1.0, unit_price=400.0, total_price=400.0),
            ],
            subtotal=400.0,
            tax=None,
            grand_total=400.0,
        )
        report = audit_offer_document(doc, "No Tax Doc")
        assert report.is_valid is True
        assert len(report.discrepancies) == 0

    def test_document_without_subtotal_computes_from_items(self):
        doc = OfferDocument(
            items=[
                LineItem(name="Item A", quantity=2.0, unit_price=150.0, total_price=300.0),
                LineItem(name="Item B", quantity=1.0, unit_price=200.0, total_price=200.0),
            ],
            subtotal=None,
            tax=50.0,
            grand_total=550.0,
        )
        report = audit_offer_document(doc, "No Subtotal Doc")
        assert report.is_valid is True
        assert len(report.discrepancies) == 0

    def test_document_with_multiple_simultaneous_errors(self):
        # Error 1: Line item 2 * 100 = 300 (expected 200)
        # Error 2: Subtotal stated 500, but sum of printed items is 300 + 100 = 400
        # Error 3: Grand total stated 700, but 500 + 50 = 550
        doc = OfferDocument(
            items=[
                LineItem(name="Item 1", quantity=2.0, unit_price=100.0, total_price=300.0),
                LineItem(name="Item 2", quantity=1.0, unit_price=100.0, total_price=100.0),
            ],
            subtotal=500.0,
            tax=50.0,
            grand_total=700.0,
        )
        report = audit_offer_document(doc, "Multi Error Doc")

        assert report.is_valid is False
        assert len(report.discrepancies) == 3
        locations = {d.location for d in report.discrepancies}
        assert locations == {"Line item: Item 1", "Subtotal", "Grand Total"}

    def test_input_document_immutability_guaranteed(self, sample_valid_document: OfferDocument):
        """
        Verify that auditing NEVER modifies or replaces numbers on the source document,
        preserving original extracted data integrity.
        """
        # Inject an intentional calculation error in line item
        sample_valid_document.items[0].total_price = 777.0
        sample_valid_document.grand_total = 9999.0

        # Snapshot before audit
        before_state = copy.deepcopy(sample_valid_document.model_dump())

        # Run audit
        report = audit_offer_document(sample_valid_document, "Immutability Check")

        # Snapshot after audit
        after_state = sample_valid_document.model_dump()

        assert before_state == after_state
        assert sample_valid_document.items[0].total_price == 777.0
        assert sample_valid_document.grand_total == 9999.0
        assert report.is_valid is False

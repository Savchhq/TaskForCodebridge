"""
Unit tests for domain schemas and data contracts.
Verifies Pydantic v2 validation, serialization, edge cases, and constraints.
"""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    AuditReport,
    ChangeType,
    ComparisonReport,
    ComparisonSummary,
    ConfidenceLevel,
    DetectedChange,
    ItemMatch,
    LineItem,
    MathDiscrepancy,
    OfferDocument,
    PageContent,
    SourceReference,
)


class TestSourceReference:
    def test_valid_source_reference(self):
        ref = SourceReference(page_number=1, snippet="Item 1: 5 x $10 = $50")
        assert ref.page_number == 1
        assert ref.snippet == "Item 1: 5 x $10 = $50"

    def test_invalid_page_number(self):
        with pytest.raises(ValidationError):
            SourceReference(page_number=0, snippet="Some text")

    def test_empty_snippet(self):
        with pytest.raises(ValidationError):
            SourceReference(page_number=1, snippet="")


class TestLineItem:
    def test_minimal_line_item(self):
        item = LineItem(name="Steel Beam")
        assert item.name == "Steel Beam"
        assert item.quantity is None
        assert item.unit_price is None
        assert item.total_price is None
        assert item.source_ref is None

    def test_full_line_item(self):
        ref = SourceReference(page_number=2, snippet="Steel Beam 10 pcs $50.00 $500.00")
        item = LineItem(
            item_id="item-001",
            name="Steel Beam",
            description="HEB 200 structural beam",
            quantity=10.0,
            unit="pcs",
            unit_price=50.0,
            total_price=500.0,
            source_ref=ref,
        )
        assert item.item_id == "item-001"
        assert item.quantity == 10.0
        assert item.unit_price == 50.0
        assert item.total_price == 500.0
        assert item.source_ref.page_number == 2

    def test_missing_name_fails(self):
        with pytest.raises(ValidationError):
            LineItem()

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError):
            LineItem(name="")


class TestOfferDocument:
    def test_minimal_offer_document(self):
        doc = OfferDocument()
        assert doc.items == []
        assert doc.vendor_name is None
        assert doc.grand_total is None

    def test_full_offer_document(self):
        item = LineItem(
            name="Consulting Services",
            quantity=40.0,
            unit="hours",
            unit_price=150.0,
            total_price=6000.0,
        )
        doc = OfferDocument(
            vendor_name="Acme Corp",
            client_name="Globex Inc",
            offer_id="OFF-2026-001",
            offer_date="2026-09-01",
            delivery_date="2026-10-01",
            currency="USD",
            items=[item],
            subtotal=6000.0,
            tax=1200.0,
            grand_total=7200.0,
        )
        assert doc.vendor_name == "Acme Corp"
        assert len(doc.items) == 1
        assert doc.grand_total == 7200.0

        # Serialization round-trip
        data = doc.model_dump()
        restored = OfferDocument.model_validate(data)
        assert restored == doc


class TestAuditModels:
    def test_math_discrepancy(self):
        disc = MathDiscrepancy(
            location="Line item: Widget X",
            expected_value=100.0,
            actual_value=120.0,
            message="Calculated quantity * price was 100.0, but PDF states 120.0",
        )
        assert disc.expected_value == 100.0
        assert disc.actual_value == 120.0

    def test_audit_report_valid(self):
        audit = AuditReport(document_name="Original Offer", is_valid=True)
        assert audit.is_valid is True
        assert audit.discrepancies == []

    def test_audit_report_with_discrepancy(self):
        disc = MathDiscrepancy(
            location="Grand Total",
            expected_value=500.0,
            actual_value=550.0,
            message="Item sum is 500.0, grand total stated is 550.0",
        )
        audit = AuditReport(
            document_name="Revised Offer",
            is_valid=False,
            discrepancies=[disc],
        )
        assert audit.is_valid is False
        assert len(audit.discrepancies) == 1


class TestChangeClassification:
    def test_change_types_enum(self):
        expected_types = {
            "ADDED",
            "REMOVED",
            "RENAMED",
            "QUANTITY_CHANGED",
            "UNIT_PRICE_CHANGED",
            "TOTAL_CHANGED",
            "DELIVERY_DATE_CHANGED",
        }
        actual_types = {t.value for t in ChangeType}
        assert expected_types == actual_types

    def test_confidence_level_enum(self):
        assert ChangeType.ADDED == "ADDED"
        assert ConfidenceLevel.CONFIRMED == "CONFIRMED"
        assert ConfidenceLevel.UNCERTAIN == "UNCERTAIN"

    def test_detected_change_creation(self):
        orig_ref = SourceReference(page_number=1, snippet="Qty: 5")
        rev_ref = SourceReference(page_number=1, snippet="Qty: 10")
        change = DetectedChange(
            change_type=ChangeType.QUANTITY_CHANGED,
            item_name_original="Server Rack",
            item_name_revised="Server Rack",
            original_value=5.0,
            revised_value=10.0,
            confidence=ConfidenceLevel.CONFIRMED,
            explanation="Quantity increased from 5 to 10 units",
            original_source_ref=orig_ref,
            revised_source_ref=rev_ref,
        )
        assert change.change_type == ChangeType.QUANTITY_CHANGED
        assert change.confidence == ConfidenceLevel.CONFIRMED
        assert change.original_value == 5.0
        assert change.revised_value == 10.0


class TestComparisonReport:
    def test_full_comparison_report(self):
        orig_audit = AuditReport(document_name="Original", is_valid=True)
        rev_audit = AuditReport(document_name="Revised", is_valid=True)

        change = DetectedChange(
            change_type=ChangeType.UNIT_PRICE_CHANGED,
            item_name_original="Widget A",
            item_name_revised="Widget A",
            original_value=10.0,
            revised_value=12.0,
            confidence=ConfidenceLevel.CONFIRMED,
            explanation="Unit price increased by $2.00",
        )

        summary = ComparisonSummary(
            total_changes=1,
            modified_items_count=1,
            has_arithmetic_errors=False,
            price_difference=20.0,
            original_grand_total=100.0,
            revised_grand_total=120.0,
            currency="USD",
        )

        report = ComparisonReport(
            original_audit=orig_audit,
            revised_audit=rev_audit,
            changes=[change],
            summary=summary,
        )

        assert report.original_audit.is_valid is True
        assert len(report.changes) == 1
        assert report.summary.total_changes == 1

        # JSON round-trip
        json_data = report.model_dump_json()
        restored = ComparisonReport.model_validate_json(json_data)
        assert restored.changes[0].change_type == ChangeType.UNIT_PRICE_CHANGED

    def test_comparison_report_accepts_dict_summary(self):
        orig_audit = AuditReport(document_name="Original", is_valid=True)
        rev_audit = AuditReport(document_name="Revised", is_valid=True)
        report = ComparisonReport(
            original_audit=orig_audit,
            revised_audit=rev_audit,
            changes=[],
            summary={"custom_key": "custom_value", "total_changes": 3},
        )
        assert report.summary.total_changes == 3


class TestAuxiliarySchemas:
    def test_page_content(self):
        page = PageContent(page_number=1, raw_text="Line 1\nLine 2", lines=["Line 1", "Line 2"])
        assert page.page_number == 1
        assert len(page.lines) == 2

    def test_item_match_valid(self):
        orig = LineItem(name="Dell XPS 15")
        rev = LineItem(name="Dell XPS 15 Laptop")
        match = ItemMatch(
            original_item=orig,
            revised_item=rev,
            confidence_score=0.95,
            confidence_level=ConfidenceLevel.CONFIRMED,
            rationale="Renamed slightly with 'Laptop' suffix",
        )
        assert match.confidence_score == 0.95
        assert match.confidence_level == ConfidenceLevel.CONFIRMED

    def test_item_match_invalid_score(self):
        with pytest.raises(ValidationError):
            ItemMatch(confidence_score=1.5)

        with pytest.raises(ValidationError):
            ItemMatch(confidence_score=-0.1)

"""
Unit tests for Diff Engine (synthesize_comparison_report).
Tests classification of all substantive change types, dual source reference attribution,
the formatting-only exemption (zero changes), and summary metrics calculation.
"""

import pytest

from app.models.schemas import (
    ChangeType,
    ConfidenceLevel,
    ItemMatch,
    LineItem,
    OfferDocument,
    PageContent,
    SourceReference,
)
from app.services.ai.base import BaseAIProvider
from app.services.diff_engine import normalize_text, synthesize_comparison_report


class StubAIProvider(BaseAIProvider):
    """Configurable test stub for AI provider to simulate deterministic scenarios."""

    def __init__(
        self,
        orig_doc: OfferDocument,
        rev_doc: OfferDocument,
        matches: list[ItemMatch],
    ) -> None:
        super().__init__()
        self._orig_doc = orig_doc
        self._rev_doc = rev_doc
        self._matches = matches

    def extract_offer_data(self, pages: list[PageContent]) -> OfferDocument:
        self._record_usage(100, 50)
        # Identify original vs revised by page content text
        full_text = " ".join(p.raw_text for p in pages)
        if "revised" in full_text.lower():
            return self._rev_doc
        return self._orig_doc

    def match_line_items(
        self,
        original_items: list[LineItem],
        revised_items: list[LineItem],
    ) -> list[ItemMatch]:
        self._record_usage(50, 30)
        return self._matches


@pytest.fixture
def base_pages():
    orig_pages = [
        PageContent(
            page_number=1,
            raw_text="Commercial Offer Original\nVendor: Acme\nDelivery: 2026-10-01\nTotal: 1000.00",
            lines=[
                "Commercial Offer Original",
                "Vendor: Acme",
                "Delivery: 2026-10-01",
                "Total: 1000.00",
            ],
        )
    ]
    rev_pages = [
        PageContent(
            page_number=1,
            raw_text="Commercial Offer Revised\nVendor: Acme\nDelivery: 2026-10-15\nTotal: 1200.00",
            lines=[
                "Commercial Offer Revised",
                "Vendor: Acme",
                "Delivery: 2026-10-15",
                "Total: 1200.00",
            ],
        )
    ]
    return orig_pages, rev_pages


class TestDiffEngineClassification:
    """Test suite verifying classification of all substantive commercial change types."""

    def test_added_and_removed_items_with_dual_source_rules(self, base_pages):
        orig_pages, rev_pages = base_pages

        removed_item = LineItem(
            name="Old Legacy Server",
            quantity=1.0,
            unit_price=300.0,
            total_price=300.0,
            source_ref=SourceReference(page_number=1, snippet="Old Legacy Server $300"),
        )
        added_item = LineItem(
            name="New Cloud Instance",
            quantity=2.0,
            unit_price=200.0,
            total_price=400.0,
            source_ref=SourceReference(page_number=1, snippet="New Cloud Instance $400"),
        )

        orig_doc = OfferDocument(
            items=[removed_item],
            subtotal=300.0,
            grand_total=300.0,
        )
        rev_doc = OfferDocument(
            items=[added_item],
            subtotal=400.0,
            grand_total=400.0,
        )

        matches = [
            ItemMatch(
                original_item=removed_item,
                revised_item=None,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
            ItemMatch(
                original_item=None,
                revised_item=added_item,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
        ]

        provider = StubAIProvider(orig_doc, rev_doc, matches)
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        # Check REMOVED change
        removed_changes = [c for c in report.changes if c.change_type == ChangeType.REMOVED]
        assert len(removed_changes) == 1
        rc = removed_changes[0]
        assert rc.item_name_original == "Old Legacy Server"
        assert rc.original_source_ref is not None
        assert rc.revised_source_ref is None

        # Check ADDED change
        added_changes = [c for c in report.changes if c.change_type == ChangeType.ADDED]
        assert len(added_changes) == 1
        ac = added_changes[0]
        assert ac.item_name_revised == "New Cloud Instance"
        assert ac.revised_source_ref is not None
        assert ac.original_source_ref is None

    def test_renamed_confirmed_and_uncertain(self, base_pages):
        orig_pages, rev_pages = base_pages

        orig_item_1 = LineItem(name="Standard Storage 500GB", quantity=1.0, unit_price=100.0, total_price=100.0)
        rev_item_1 = LineItem(name="Cloud Storage Tier Alpha (500GB)", quantity=1.0, unit_price=100.0, total_price=100.0)

        orig_item_2 = LineItem(name="Basic Support", quantity=1.0, unit_price=50.0, total_price=50.0)
        rev_item_2 = LineItem(name="Ambiguous IT Maintenance", quantity=1.0, unit_price=50.0, total_price=50.0)

        orig_doc = OfferDocument(items=[orig_item_1, orig_item_2], grand_total=150.0)
        rev_doc = OfferDocument(items=[rev_item_1, rev_item_2], grand_total=150.0)

        matches = [
            ItemMatch(
                original_item=orig_item_1,
                revised_item=rev_item_1,
                confidence_score=0.92,
                confidence_level=ConfidenceLevel.CONFIRMED,
                rationale="Semantically identical storage tier",
            ),
            ItemMatch(
                original_item=orig_item_2,
                revised_item=rev_item_2,
                confidence_score=0.65,
                confidence_level=ConfidenceLevel.UNCERTAIN,
                rationale="Ambiguous service scope",
            ),
        ]

        provider = StubAIProvider(orig_doc, rev_doc, matches)
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        renamed = [c for c in report.changes if c.change_type == ChangeType.RENAMED]
        assert len(renamed) == 2

        # 1st rename: CONFIRMED (score >= 0.8)
        assert renamed[0].confidence == ConfidenceLevel.CONFIRMED
        assert renamed[0].item_name_original == "Standard Storage 500GB"
        assert renamed[0].item_name_revised == "Cloud Storage Tier Alpha (500GB)"
        assert renamed[0].original_source_ref is not None
        assert renamed[0].revised_source_ref is not None

        # 2nd rename: UNCERTAIN (score < 0.8)
        assert renamed[1].confidence == ConfidenceLevel.UNCERTAIN
        assert renamed[1].item_name_original == "Basic Support"
        assert renamed[1].item_name_revised == "Ambiguous IT Maintenance"
        assert renamed[1].original_source_ref is not None
        assert renamed[1].revised_source_ref is not None

    def test_quantity_and_unit_price_changes(self, base_pages):
        orig_pages, rev_pages = base_pages

        orig_item = LineItem(name="Widget A", quantity=5.0, unit_price=10.0, total_price=50.0)
        rev_item = LineItem(name="Widget A", quantity=8.0, unit_price=12.5, total_price=100.0)

        orig_doc = OfferDocument(items=[orig_item], grand_total=50.0)
        rev_doc = OfferDocument(items=[rev_item], grand_total=100.0)

        matches = [
            ItemMatch(
                original_item=orig_item,
                revised_item=rev_item,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            )
        ]

        provider = StubAIProvider(orig_doc, rev_doc, matches)
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        qty_change = next(c for c in report.changes if c.change_type == ChangeType.QUANTITY_CHANGED)
        assert qty_change.original_value == 5.0
        assert qty_change.revised_value == 8.0
        assert qty_change.original_source_ref is not None
        assert qty_change.revised_source_ref is not None

        price_change = next(c for c in report.changes if c.change_type == ChangeType.UNIT_PRICE_CHANGED)
        assert price_change.original_value == 10.0
        assert price_change.revised_value == 12.5
        assert price_change.original_source_ref is not None
        assert price_change.revised_source_ref is not None

    def test_delivery_date_change(self, base_pages):
        orig_pages, rev_pages = base_pages

        orig_doc = OfferDocument(delivery_date="2026-10-01", grand_total=100.0)
        rev_doc = OfferDocument(delivery_date="2026-10-20", grand_total=100.0)

        provider = StubAIProvider(orig_doc, rev_doc, [])
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        date_changes = [c for c in report.changes if c.change_type == ChangeType.DELIVERY_DATE_CHANGED]
        assert len(date_changes) == 1
        dc = date_changes[0]
        assert dc.original_value == "2026-10-01"
        assert dc.revised_value == "2026-10-20"
        assert dc.original_source_ref is not None
        assert dc.revised_source_ref is not None


class TestFormattingExemption:
    """Test suite ensuring formatting-only differences produce exactly ZERO changes."""

    def test_reformatted_variant_produces_zero_changes(self, base_pages):
        orig_pages, rev_pages = base_pages

        # Same semantic content with different casing, whitespace, and column order
        orig_item_1 = LineItem(name="Enterprise Cloud Server", quantity=2.0, unit_price=500.0, total_price=1000.0)
        orig_item_2 = LineItem(name="Database Backup Service", quantity=1.0, unit_price=200.0, total_price=200.0)

        # Revised: same items reordered and with extra whitespace / capitalization
        rev_item_2 = LineItem(name="database  backup   service", quantity=1.0, unit_price=200.0, total_price=200.0)
        rev_item_1 = LineItem(name="ENTERPRISE CLOUD SERVER", quantity=2.0, unit_price=500.0, total_price=1000.0)

        orig_doc = OfferDocument(
            items=[orig_item_1, orig_item_2],
            delivery_date="2026-10-01",
            subtotal=1200.0,
            grand_total=1200.0,
        )
        rev_doc = OfferDocument(
            items=[rev_item_2, rev_item_1],
            delivery_date="  2026-10-01  ",
            subtotal=1200.0,
            grand_total=1200.0,
        )

        matches = [
            ItemMatch(
                original_item=orig_item_1,
                revised_item=rev_item_1,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
            ItemMatch(
                original_item=orig_item_2,
                revised_item=rev_item_2,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
        ]

        provider = StubAIProvider(orig_doc, rev_doc, matches)
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        # STRICT REQUIREMENT: zero substantive changes!
        assert len(report.changes) == 0
        assert report.summary.total_changes == 0
        assert report.summary.added_items_count == 0
        assert report.summary.removed_items_count == 0
        assert report.summary.modified_items_count == 0


class TestComparisonSummaryMetrics:
    """Test suite verifying summary calculations, speed, and token cost metrics."""

    def test_summary_metrics_assembly(self, base_pages):
        orig_pages, rev_pages = base_pages

        orig_doc = OfferDocument(
            items=[
                LineItem(name="Item 1", quantity=1.0, unit_price=100.0, total_price=100.0),
                LineItem(name="Item 2", quantity=2.0, unit_price=50.0, total_price=100.0),
            ],
            grand_total=200.0,
            currency="USD",
        )
        rev_doc = OfferDocument(
            items=[
                LineItem(name="Item 1", quantity=1.0, unit_price=120.0, total_price=120.0),  # price changed
                LineItem(name="Item 3", quantity=1.0, unit_price=80.0, total_price=80.0),    # added
            ],
            grand_total=200.0,
            currency="USD",
        )

        matches = [
            ItemMatch(
                original_item=orig_doc.items[0],
                revised_item=rev_doc.items[0],
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
            ItemMatch(
                original_item=orig_doc.items[1],
                revised_item=None,
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
            ItemMatch(
                original_item=None,
                revised_item=rev_doc.items[1],
                confidence_score=1.0,
                confidence_level=ConfidenceLevel.CONFIRMED,
            ),
        ]

        provider = StubAIProvider(orig_doc, rev_doc, matches)
        report = synthesize_comparison_report(orig_pages, rev_pages, provider)

        summary = report.summary
        assert summary.added_items_count == 1
        assert summary.removed_items_count == 1
        assert summary.modified_items_count == 1  # unit price changed
        assert summary.total_changes == 3
        assert summary.price_difference == 0.0
        assert summary.processing_time_ms is not None and summary.processing_time_ms >= 0
        assert summary.token_usage is not None
        assert summary.token_usage.total_tokens > 0
        assert summary.estimated_cost_usd is not None

"""
Diff Engine service for commercial offer comparison.
Synthesizes extracted data, deterministic math audit, and semantic matching
into a categorized substantive change report adhering to the strict formatting exemption
and dual source reference attribution rules.
"""

from __future__ import annotations

import re
import time

from app.models.schemas import (
    ChangeType,
    ComparisonReport,
    ComparisonSummary,
    ConfidenceLevel,
    DetectedChange,
    ItemMatch,
    LineItem,
    PageContent,
    SourceReference,
)
from app.services.ai.base import BaseAIProvider
from app.services.auditor import audit_offer_document
from app.services.pdf_extractor import find_source_snippet


def normalize_text(text: str | None) -> str:
    """
    Normalize text by trimming, lowercasing, and collapsing whitespace.
    Used for formatting-exemption comparisons.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip()).lower()


def get_or_find_source_ref(
    item: LineItem | None,
    pages: list[PageContent],
    fallback_query: str = "",
) -> SourceReference | None:
    """
    Ensure every substantive change has a traceable, non-null source reference.
    Prefers item.source_ref, searches page content, or falls back to top page lines.
    """
    if item is not None and item.source_ref is not None:
        return item.source_ref

    query = (item.name if item is not None else "") or fallback_query
    if query:
        ref = find_source_snippet(pages, query)
        if ref is not None:
            return ref

    # Fallback to the first available line in pages
    if pages:
        first_page = pages[0]
        snippet = (
            first_page.lines[0]
            if first_page.lines
            else (first_page.raw_text[:120].strip() or "Source document reference")
        )
        return SourceReference(page_number=first_page.page_number, snippet=snippet)

    return SourceReference(page_number=1, snippet="Source document reference")


def synthesize_comparison_report(
    original_pages: list[PageContent],
    revised_pages: list[PageContent],
    ai_provider: BaseAIProvider,
) -> ComparisonReport:
    """
    Synthesize end-to-end commercial comparison between original and revised offers.

    Steps:
    1. Extract structured offer data for both documents via AI provider.
    2. Deterministically audit arithmetic in both documents.
    3. Match line items semantically across documents.
    4. Categorize substantive changes (Added, Removed, Renamed, Qty, Price, Totals, Delivery).
    5. Enforce Formatting Exemption: differences only in whitespace/layout/casing produce 0 changes.
    6. Enforce Dual Source References for all modifications.
    7. Assemble ComparisonSummary with performance and token metrics.

    Args:
        original_pages: Extracted pages from original PDF.
        revised_pages: Extracted pages from revised PDF.
        ai_provider: AI Provider instance (e.g. GeminiFlashProvider or MockAIProvider).

    Returns:
        Complete, validated ComparisonReport.
    """
    start_time = time.perf_counter()

    # 1. AI Extraction
    original_doc = ai_provider.extract_offer_data(original_pages)
    revised_doc = ai_provider.extract_offer_data(revised_pages)

    # 2. Deterministic Math Audit (pure Python)
    original_audit = audit_offer_document(original_doc, "Original Offer")
    revised_audit = audit_offer_document(revised_doc, "Revised Offer")

    # 3. Semantic Line Item Matching
    matches: list[ItemMatch] = ai_provider.match_line_items(
        original_doc.items, revised_doc.items
    )

    # Identify any revised line items that contain arithmetic discrepancies
    erroneous_rev_items = {
        d.location.replace("Line item: ", "").strip().lower()
        for d in revised_audit.discrepancies
        if d.location.startswith("Line item:")
    }

    # 4. Substantive Change Classification
    changes: list[DetectedChange] = []

    for match in matches:
        orig = match.original_item
        rev = match.revised_item

        # Case A: Added item
        if orig is None and rev is not None:
            changes.append(
                DetectedChange(
                    change_type=ChangeType.ADDED,
                    item_name_original=None,
                    item_name_revised=rev.name,
                    original_value=None,
                    revised_value={
                        "quantity": rev.quantity,
                        "unit_price": rev.unit_price,
                        "total_price": rev.total_price,
                    },
                    confidence=match.confidence_level,
                    explanation=f"New line item '{rev.name}' was added to the revised offer.",
                    original_source_ref=None,
                    revised_source_ref=get_or_find_source_ref(rev, revised_pages),
                )
            )
            continue

        # Case B: Removed item
        if orig is not None and rev is None:
            changes.append(
                DetectedChange(
                    change_type=ChangeType.REMOVED,
                    item_name_original=orig.name,
                    item_name_revised=None,
                    original_value={
                        "quantity": orig.quantity,
                        "unit_price": orig.unit_price,
                        "total_price": orig.total_price,
                    },
                    revised_value=None,
                    confidence=match.confidence_level,
                    explanation=f"Line item '{orig.name}' was removed from the revised offer.",
                    original_source_ref=get_or_find_source_ref(orig, original_pages),
                    revised_source_ref=None,
                )
            )
            continue

        # Case C: Both items present
        if orig is not None and rev is not None:
            # 1. Check Renamed (Formatting exemption: casing & extra whitespace are ignored)
            if normalize_text(orig.name) != normalize_text(rev.name):
                conf = (
                    ConfidenceLevel.CONFIRMED
                    if match.confidence_score >= 0.8
                    else ConfidenceLevel.UNCERTAIN
                )
                rationale_text = f" ({match.rationale})" if match.rationale else ""
                changes.append(
                    DetectedChange(
                        change_type=ChangeType.RENAMED,
                        item_name_original=orig.name,
                        item_name_revised=rev.name,
                        original_value=orig.name,
                        revised_value=rev.name,
                        confidence=conf,
                        explanation=f"Item renamed from '{orig.name}' to '{rev.name}'{rationale_text}.",
                        original_source_ref=get_or_find_source_ref(orig, original_pages),
                        revised_source_ref=get_or_find_source_ref(rev, revised_pages),
                    )
                )

            # 2. Check Quantity Changed
            qty_changed = False
            if (
                orig.quantity is not None
                and rev.quantity is not None
                and abs(orig.quantity - rev.quantity) > 1e-4
            ):
                qty_changed = True
                changes.append(
                    DetectedChange(
                        change_type=ChangeType.QUANTITY_CHANGED,
                        item_name_original=orig.name,
                        item_name_revised=rev.name,
                        original_value=orig.quantity,
                        revised_value=rev.quantity,
                        confidence=match.confidence_level,
                        explanation=(
                            f"Quantity changed from {orig.quantity} to {rev.quantity} "
                            f"for '{rev.name}'."
                        ),
                        original_source_ref=get_or_find_source_ref(orig, original_pages),
                        revised_source_ref=get_or_find_source_ref(rev, revised_pages),
                    )
                )

            # 3. Check Unit Price Changed
            # If line item has a calculation error in revised doc but line total is unchanged,
            # it is a source arithmetic discrepancy rather than an agreed commercial change.
            is_math_error_item = (
                rev.name.strip().lower() in erroneous_rev_items
                and orig.total_price is not None
                and rev.total_price is not None
                and abs(orig.total_price - rev.total_price) <= 0.01
            )
            price_changed = False
            if (
                not is_math_error_item
                and orig.unit_price is not None
                and rev.unit_price is not None
                and abs(orig.unit_price - rev.unit_price) > 0.01
            ):
                price_changed = True
                changes.append(
                    DetectedChange(
                        change_type=ChangeType.UNIT_PRICE_CHANGED,
                        item_name_original=orig.name,
                        item_name_revised=rev.name,
                        original_value=orig.unit_price,
                        revised_value=rev.unit_price,
                        confidence=match.confidence_level,
                        explanation=(
                            f"Unit price changed from {orig.unit_price:.2f} to {rev.unit_price:.2f} "
                            f"for '{rev.name}'."
                        ),
                        original_source_ref=get_or_find_source_ref(orig, original_pages),
                        revised_source_ref=get_or_find_source_ref(rev, revised_pages),
                    )
                )

            # 4. Check Line Item Total Changed (if neither qty nor unit price changed)
            if not qty_changed and not price_changed:
                if (
                    orig.total_price is not None
                    and rev.total_price is not None
                    and abs(orig.total_price - rev.total_price) > 0.01
                ):
                    changes.append(
                        DetectedChange(
                            change_type=ChangeType.TOTAL_CHANGED,
                            item_name_original=orig.name,
                            item_name_revised=rev.name,
                            original_value=orig.total_price,
                            revised_value=rev.total_price,
                            confidence=match.confidence_level,
                            explanation=(
                                f"Line total changed from {orig.total_price:.2f} to "
                                f"{rev.total_price:.2f} for '{rev.name}'."
                            ),
                            original_source_ref=get_or_find_source_ref(orig, original_pages),
                            revised_source_ref=get_or_find_source_ref(rev, revised_pages),
                        )
                    )

    # 5. Check Document-Level Delivery Date Change
    if (
        normalize_text(original_doc.delivery_date)
        != normalize_text(revised_doc.delivery_date)
        and (original_doc.delivery_date or revised_doc.delivery_date)
    ):
        changes.append(
            DetectedChange(
                change_type=ChangeType.DELIVERY_DATE_CHANGED,
                item_name_original="Delivery Date",
                item_name_revised="Delivery Date",
                original_value=original_doc.delivery_date,
                revised_value=revised_doc.delivery_date,
                confidence=ConfidenceLevel.CONFIRMED,
                explanation=(
                    f"Delivery date changed from '{original_doc.delivery_date}' to "
                    f"'{revised_doc.delivery_date}'."
                ),
                original_source_ref=get_or_find_source_ref(
                    None, original_pages, fallback_query=original_doc.delivery_date or "Delivery"
                ),
                revised_source_ref=get_or_find_source_ref(
                    None, revised_pages, fallback_query=revised_doc.delivery_date or "Delivery"
                ),
            )
        )

    # 6. Check Document-Level Grand Total Change
    if (
        original_doc.grand_total is not None
        and revised_doc.grand_total is not None
        and abs(original_doc.grand_total - revised_doc.grand_total) > 0.01
    ):
        currency_str = f" {revised_doc.currency or original_doc.currency or ''}".rstrip()
        changes.append(
            DetectedChange(
                change_type=ChangeType.TOTAL_CHANGED,
                item_name_original="Grand Total",
                item_name_revised="Grand Total",
                original_value=original_doc.grand_total,
                revised_value=revised_doc.grand_total,
                confidence=ConfidenceLevel.CONFIRMED,
                explanation=(
                    f"Grand total changed from {original_doc.grand_total:.2f} to "
                    f"{revised_doc.grand_total:.2f}{currency_str}."
                ),
                original_source_ref=get_or_find_source_ref(
                    None, original_pages, fallback_query=str(original_doc.grand_total)
                ),
                revised_source_ref=get_or_find_source_ref(
                    None, revised_pages, fallback_query=str(revised_doc.grand_total)
                ),
            )
        )

    # 7. Assemble Performance & Cost Metrics
    processing_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    token_usage = ai_provider.cumulative_token_usage
    estimated_cost_usd = token_usage.estimated_cost_usd

    orig_total = original_doc.grand_total
    rev_total = revised_doc.grand_total
    price_diff = (
        round(rev_total - orig_total, 2)
        if (orig_total is not None and rev_total is not None)
        else None
    )

    summary = ComparisonSummary(
        total_changes=len(changes),
        added_items_count=sum(1 for c in changes if c.change_type == ChangeType.ADDED),
        removed_items_count=sum(1 for c in changes if c.change_type == ChangeType.REMOVED),
        modified_items_count=sum(
            1
            for c in changes
            if c.change_type not in (ChangeType.ADDED, ChangeType.REMOVED)
        ),
        has_arithmetic_errors=not (original_audit.is_valid and revised_audit.is_valid),
        price_difference=price_diff,
        original_grand_total=orig_total,
        revised_grand_total=rev_total,
        currency=revised_doc.currency or original_doc.currency,
        processing_time_ms=processing_time_ms,
        token_usage=token_usage,
        estimated_cost_usd=estimated_cost_usd,
    )

    return ComparisonReport(
        original_document=original_doc,
        revised_document=revised_doc,
        original_audit=original_audit,
        revised_audit=revised_audit,
        changes=changes,
        summary=summary,
        processing_time_ms=processing_time_ms,
        token_usage=token_usage,
        estimated_cost_usd=estimated_cost_usd,
    )

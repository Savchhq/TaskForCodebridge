"""
Deterministic mathematical verification engine.
Audits line item arithmetic (quantity * unit_price == total) and document totals
(sum of line items == subtotal, subtotal + tax == grand_total) using pure Python.
Never overwrites or alters original document data.
"""

from __future__ import annotations

from app.models.schemas import AuditReport, LineItem, MathDiscrepancy, OfferDocument

# Tolerance threshold for floating-point currency calculations (1 cent)
CALCULATION_TOLERANCE = 0.01


def audit_line_item(item: LineItem) -> list[MathDiscrepancy]:
    """
    Deterministically verify a single line item's multiplication arithmetic:
    quantity * unit_price == total_price.

    Args:
        item: The line item to audit.

    Returns:
        List of detected MathDiscrepancy objects (empty if valid or missing data).
    """
    discrepancies: list[MathDiscrepancy] = []

    if item.quantity is not None and item.unit_price is not None and item.total_price is not None:
        expected = round(item.quantity * item.unit_price, 2)
        diff = round(abs(item.total_price - expected), 4)

        if diff > CALCULATION_TOLERANCE:
            location_name = f"Line item: {item.name}"
            msg = (
                f"Calculation mismatch for '{item.name}': "
                f"expected {expected:.2f} ({item.quantity} * {item.unit_price:.2f}), "
                f"but document states {item.total_price:.2f}"
            )
            discrepancies.append(
                MathDiscrepancy(
                    location=location_name,
                    expected_value=expected,
                    actual_value=item.total_price,
                    message=msg,
                )
            )

    return discrepancies


def audit_offer_document(
    doc: OfferDocument,
    doc_name: str = "Document",
) -> AuditReport:
    """
    Deterministically audit all arithmetic in an offer document:
    1. Line item arithmetic (qty * unit_price == total_price)
    2. Document subtotal == sum of line items
    3. Document grand total == subtotal + tax

    Strict Integrity Rule:
    Does NOT modify or overwrite any numbers on `doc`.

    Args:
        doc: The OfferDocument to verify.
        doc_name: Human-readable document identifier (e.g. 'Original Offer', 'Revised Offer').

    Returns:
        AuditReport detailing whether document is valid and any discrepancies found.
    """
    discrepancies: list[MathDiscrepancy] = []

    # 1. Audit each line item
    for item in doc.items:
        discrepancies.extend(audit_line_item(item))

    # Calculate effective item totals for document level sums
    item_totals: list[float] = []
    for item in doc.items:
        if item.total_price is not None:
            item_totals.append(item.total_price)
        elif item.quantity is not None and item.unit_price is not None:
            item_totals.append(round(item.quantity * item.unit_price, 2))

    calculated_items_sum = round(sum(item_totals), 2) if item_totals else None

    # 2. Audit subtotal against sum of line items
    if doc.subtotal is not None and calculated_items_sum is not None:
        diff_subtotal = round(abs(doc.subtotal - calculated_items_sum), 4)
        if diff_subtotal > CALCULATION_TOLERANCE:
            discrepancies.append(
                MathDiscrepancy(
                    location="Subtotal",
                    expected_value=calculated_items_sum,
                    actual_value=doc.subtotal,
                    message=(
                        f"Subtotal mismatch: expected {calculated_items_sum:.2f} "
                        f"(sum of line items), but document states {doc.subtotal:.2f}"
                    ),
                )
            )

    # 3. Audit grand total against subtotal + tax (or items sum + tax if subtotal omitted)
    if doc.grand_total is not None:
        base_amount = doc.subtotal if doc.subtotal is not None else calculated_items_sum
        if base_amount is not None:
            tax_amount = doc.tax if doc.tax is not None else 0.0
            expected_grand_total = round(base_amount + tax_amount, 2)
            diff_grand = round(abs(doc.grand_total - expected_grand_total), 4)

            if diff_grand > CALCULATION_TOLERANCE:
                if doc.tax is not None:
                    breakdown_msg = f"{base_amount:.2f} base + {tax_amount:.2f} tax"
                else:
                    breakdown_msg = f"{base_amount:.2f} base (no tax)"

                discrepancies.append(
                    MathDiscrepancy(
                        location="Grand Total",
                        expected_value=expected_grand_total,
                        actual_value=doc.grand_total,
                        message=(
                            f"Grand total mismatch: expected {expected_grand_total:.2f} "
                            f"({breakdown_msg}), but document states {doc.grand_total:.2f}"
                        ),
                    )
                )

    return AuditReport(
        document_name=doc_name,
        is_valid=(len(discrepancies) == 0),
        discrepancies=discrepancies,
    )

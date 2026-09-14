"""
Synthetic Test PDF Generator for Commercial Offer Comparison.

Generates reproducible, realistic commercial offer PDF pairs according to project specifications:
- Scenario 1 (Main Commercial Pair):
    * offer_v1.pdf: Baseline commercial proposal (IT/Cloud Infrastructure, 6 items).
    * offer_v2_substantive.pdf: Revised proposal containing 1 renamed item, reordered lines,
      1 quantity change, 1 unit price change, 1 removed item, 1 added item,
      1 delivery date change, 1 deliberate arithmetic error ($1,200 instead of $1,000),
      and distinct styling/formatting.
- Scenario 2 (Formatting-Only Variation):
    * offer_v1_reformatted.pdf: Exact same commercial data as offer_v1.pdf with
      a modern minimalist layout and typography. Yields exactly ZERO commercial changes.
- Scenario 3 (Ambiguity / Clarification):
    * offer_v2_ambiguous.pdf: Revised proposal containing an ambiguous line item
      lacking an explicit SKU, requiring UNCERTAIN confidence classification.

Also generates test_fixtures/samples/ground_truth.json containing structured
authoritative benchmarks for all three test scenarios.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pdfplumber
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent
SAMPLES_DIR = BASE_DIR / "samples"
GROUND_TRUTH_PATH = SAMPLES_DIR / "ground_truth.json"


def _format_currency(val: float | int | None) -> str:
    if val is None:
        return "$0.00"
    return f"${val:,.2f}"


def build_offer_v1(output_path: Path) -> None:
    """Generate offer_v1.pdf: Baseline IT/Cloud commercial offer."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "V1_Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
    )
    subtitle_style = ParagraphStyle(
        "V1_Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
    )
    meta_label_style = ParagraphStyle(
        "V1_MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E3A8A"),
    )
    meta_val_style = ParagraphStyle(
        "V1_MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
    )
    th_style = ParagraphStyle(
        "V1_TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=0,
    )
    th_right_style = ParagraphStyle(
        "V1_THRight",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=2,
    )
    th_center_style = ParagraphStyle(
        "V1_THCenter",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1,
    )
    td_name_style = ParagraphStyle(
        "V1_TDName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    td_desc_style = ParagraphStyle(
        "V1_TDDesc",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
    )
    td_text_style = ParagraphStyle(
        "V1_TDText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
    )
    td_right_style = ParagraphStyle(
        "V1_TDRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=2,
    )
    td_center_style = ParagraphStyle(
        "V1_TDCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=1,
    )
    total_label_style = ParagraphStyle(
        "V1_TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=2,
    )
    total_val_style = ParagraphStyle(
        "V1_TotalVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
        alignment=2,
    )

    story = []

    # Header section
    story.append(Paragraph("COMMERCIAL PROPOSAL / SERVICE OFFER", title_style))
    story.append(Paragraph("Cloud Infrastructure & Enterprise Managed Services", subtitle_style))
    story.append(Spacer(1, 14))

    # Metadata cards (Vendor on Left, Client & Offer Details on Right)
    vendor_block = [
        Paragraph("<b>VENDOR / PROVIDER:</b>", meta_label_style),
        Paragraph("CloudScale Technologies Inc.", meta_val_style),
        Paragraph("100 Enterprise Way, Suite 400", meta_val_style),
        Paragraph("San Francisco, CA 94105", meta_val_style),
        Paragraph("Contact: sales@cloudscale-tech.example", meta_val_style),
    ]
    client_block = [
        Paragraph("<b>CLIENT / RECIPIENT:</b>", meta_label_style),
        Paragraph("Acme Global Logistics LLC", meta_val_style),
        Paragraph("742 Market Boulevard, Chicago, IL 60601", meta_val_style),
        Paragraph("Attn: Procurement & Cloud Infrastructure Team", meta_val_style),
    ]
    details_block = [
        Paragraph("<b>OFFER DETAILS:</b>", meta_label_style),
        Paragraph("Offer ID: <b>CST-2026-0891</b>", meta_val_style),
        Paragraph("Issue Date: <b>2026-09-01</b>", meta_val_style),
        Paragraph("Delivery Date: <b>2026-10-15</b>", meta_val_style),
        Paragraph("Currency: <b>USD ($)</b> | Terms: <b>Net 30</b>", meta_val_style),
    ]

    meta_table = Table(
        [[vendor_block, client_block, details_block]],
        colWidths=[175, 185, 180],
    )
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # Items table header
    table_data = [[
        Paragraph("#", th_center_style),
        Paragraph("Line Item & Specification", th_style),
        Paragraph("Qty", th_right_style),
        Paragraph("Unit", th_center_style),
        Paragraph("Unit Price", th_right_style),
        Paragraph("Total Price", th_right_style),
    ]]

    # 6 Baseline Items
    v1_items = [
        (
            1,
            "Dedicated Cloud Compute Node (c6i.4xlarge)",
            "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
            4,
            "nodes",
            450.00,
            1800.00,
        ),
        (
            2,
            "Managed Kubernetes Control Plane",
            "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
            2,
            "clusters",
            300.00,
            600.00,
        ),
        (
            3,
            "High-Performance NVMe Block Storage (5TB)",
            "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
            3,
            "volumes",
            250.00,
            750.00,
        ),
        (
            4,
            "Multi-Region Cloud Load Balancer",
            "Layer 4/7 global traffic director with SSL offloading and automated health probing",
            2,
            "units",
            150.00,
            300.00,
        ),
        (
            5,
            "Cloud Security & DDoS Shield Enterprise",
            "Automated WAF rulesets, volumetric DDoS mitigation, and intrusion prevention inspection",
            1,
            "license",
            850.00,
            850.00,
        ),
        (
            6,
            "24/7 DevOps Support & SLA Package",
            "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
            1,
            "month",
            1200.00,
            1200.00,
        ),
    ]

    for idx, name, desc, qty, unit, unit_price, total in v1_items:
        item_cell = [
            Paragraph(name, td_name_style),
            Paragraph(desc, td_desc_style),
        ]
        table_data.append([
            Paragraph(str(idx), td_center_style),
            item_cell,
            Paragraph(str(qty), td_right_style),
            Paragraph(unit, td_center_style),
            Paragraph(_format_currency(unit_price), td_right_style),
            Paragraph(_format_currency(total), td_right_style),
        ])

    items_table = Table(
        table_data,
        colWidths=[25, 245, 40, 50, 90, 90],
    )
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Totals block
    totals_data = [
        [Paragraph("Subtotal:", total_label_style), Paragraph(_format_currency(5500.00), total_val_style)],
        [Paragraph("Estimated Tax (0.0%):", total_label_style), Paragraph(_format_currency(0.00), total_val_style)],
        [Paragraph("Grand Total (USD):", total_label_style), Paragraph(_format_currency(5500.00), total_val_style)],
    ]
    totals_table = Table(totals_data, colWidths=[450, 90])
    totals_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEABOVE", (0, 2), (1, 2), 1, colors.HexColor("#1E3A8A")),
        ])
    )
    story.append(KeepTogether([totals_table]))
    story.append(Spacer(1, 20))

    # Acceptance / Signature note
    notes = [
        Paragraph("<b>Terms & Conditions:</b>", td_name_style),
        Paragraph(
            "This offer is valid for 30 calendar days from issue date. All services are governed by the Enterprise Cloud "
            "Master Service Agreement. Final billing is based on agreed monthly recurring and provisioned capacity.",
            td_desc_style,
        ),
        Spacer(1, 14),
        Paragraph("Authorized Provider Representative: <i>Marcus Vance, VP Enterprise Cloud Solutions</i>", td_desc_style),
    ]
    story.append(KeepTogether(notes))

    doc.build(story)


def build_offer_v2_substantive(output_path: Path) -> None:
    """
    Generate offer_v2_substantive.pdf: Revised offer containing:
    1. Renamed item ('Managed Kubernetes Control Plane' -> 'K8s Managed Control Plane & Orchestrator')
    2. Reordered rows
    3. 1 Quantity change (Dedicated Cloud Compute Node: 4 -> 6)
    4. 1 Unit price change (Cloud Security & DDoS Shield Enterprise: $850 -> $950)
    5. 1 Removed position (Multi-Region Cloud Load Balancer)
    6. 1 Added position (Automated Disaster Recovery & Backup Replication)
    7. 1 Delivery date change (2026-10-15 -> 2026-11-01)
    8. 1 Deliberate calculation mistake in line item 24/7 DevOps Support ($1,000 unit price * 1 qty printed as $1,200)
    9. Distinct layout, fonts (Times-Roman / Times-Bold), and green/slate styling.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Distinct typography and color scheme (Emerald / Slate)
    title_style = ParagraphStyle(
        "V2_Title",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#065F46"),
    )
    subtitle_style = ParagraphStyle(
        "V2_Subtitle",
        parent=styles["Normal"],
        fontName="Times-Italic",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#374151"),
    )
    meta_label_style = ParagraphStyle(
        "V2_MetaLabel",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#065F46"),
    )
    meta_val_style = ParagraphStyle(
        "V2_MetaVal",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
    )
    th_style = ParagraphStyle(
        "V2_TH",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=0,
    )
    th_right_style = ParagraphStyle(
        "V2_THRight",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=2,
    )
    th_center_style = ParagraphStyle(
        "V2_THCenter",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1,
    )
    td_name_style = ParagraphStyle(
        "V2_TDName",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    td_desc_style = ParagraphStyle(
        "V2_TDDesc",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
    )
    td_right_style = ParagraphStyle(
        "V2_TDRight",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=2,
    )
    td_center_style = ParagraphStyle(
        "V2_TDCenter",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=1,
    )
    total_label_style = ParagraphStyle(
        "V2_TotalLabel",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#065F46"),
        alignment=2,
    )
    total_val_style = ParagraphStyle(
        "V2_TotalVal",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
        alignment=2,
    )

    story = []

    # Title Banner
    story.append(Paragraph("REVISED COMMERCIAL OFFER (REV-1)", title_style))
    story.append(Paragraph("Updated Scope, Specifications & Schedule Breakdown", subtitle_style))
    story.append(Spacer(1, 14))

    # Metadata Block
    vendor_block = [
        Paragraph("<b>VENDOR / PROVIDER:</b>", meta_label_style),
        Paragraph("CloudScale Technologies Inc.", meta_val_style),
        Paragraph("100 Enterprise Way, Suite 400", meta_val_style),
        Paragraph("San Francisco, CA 94105", meta_val_style),
        Paragraph("Contact: sales@cloudscale-tech.example", meta_val_style),
    ]
    client_block = [
        Paragraph("<b>CLIENT / RECIPIENT:</b>", meta_label_style),
        Paragraph("Acme Global Logistics LLC", meta_val_style),
        Paragraph("742 Market Boulevard, Chicago, IL 60601", meta_val_style),
        Paragraph("Attn: Procurement & Cloud Infrastructure Team", meta_val_style),
    ]
    # NOTE: Delivery Date changed from 2026-10-15 to 2026-11-01
    details_block = [
        Paragraph("<b>OFFER DETAILS:</b>", meta_label_style),
        Paragraph("Offer ID: <b>CST-2026-0891-REV1</b>", meta_val_style),
        Paragraph("Issue Date: <b>2026-09-10</b>", meta_val_style),
        Paragraph("Delivery Date: <b>2026-11-01</b>", meta_val_style),
        Paragraph("Currency: <b>USD ($)</b> | Terms: <b>Net 30</b>", meta_val_style),
    ]

    meta_table = Table(
        [[vendor_block, client_block, details_block]],
        colWidths=[175, 185, 180],
    )
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BBF7D0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # Items Table Header
    table_data = [[
        Paragraph("Pos", th_center_style),
        Paragraph("Line Item & Specification", th_style),
        Paragraph("Quantity", th_right_style),
        Paragraph("Unit", th_center_style),
        Paragraph("Unit Price", th_right_style),
        Paragraph("Total Price", th_right_style),
    ]]

    # Items with deliberate modifications & reordering:
    # 1. Dedicated Cloud Compute Node: Qty increased 4 -> 6 (Total: $2,700.00)
    # 2. Cloud Security & DDoS Shield: Unit price changed $850.00 -> $950.00 (Total: $950.00)
    # 3. K8s Managed Control Plane & Orchestrator: Renamed from 'Managed Kubernetes Control Plane' (Total: $600.00)
    # 4. Automated Disaster Recovery & Backup Replication: ADDED new line item ($500.00)
    # 5. High-Performance NVMe Block Storage (5TB): Unchanged, reordered ($750.00)
    # 6. 24/7 DevOps Support & SLA Package: Unit price $1,000.00, printed total $1,200.00 (ARITHMETIC ERROR: $1,200 instead of $1,000!)
    # REMOVED: Multi-Region Cloud Load Balancer ($300.00) is absent.
    v2_items = [
        (
            1,
            "Dedicated Cloud Compute Node (c6i.4xlarge)",
            "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
            6,
            "nodes",
            450.00,
            2700.00,
        ),
        (
            2,
            "Cloud Security & DDoS Shield Enterprise",
            "Automated WAF rulesets, volumetric DDoS mitigation, and intrusion prevention inspection",
            1,
            "license",
            950.00,
            950.00,
        ),
        (
            3,
            "K8s Managed Control Plane & Orchestrator",
            "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
            2,
            "clusters",
            300.00,
            600.00,
        ),
        (
            4,
            "Automated Disaster Recovery & Backup Replication",
            "Cross-region continuous data replication with 15-minute RPO and 1-hour RTO",
            1,
            "service",
            500.00,
            500.00,
        ),
        (
            5,
            "High-Performance NVMe Block Storage (5TB)",
            "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
            3,
            "volumes",
            250.00,
            750.00,
        ),
        (
            6,
            "24/7 DevOps Support & SLA Package",
            "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
            1,
            "month",
            1000.00,
            1200.00,  # DELIBERATE MATH ERROR: 1 * 1,000.00 != 1,200.00
        ),
    ]

    for idx, name, desc, qty, unit, unit_price, total in v2_items:
        item_cell = [
            Paragraph(name, td_name_style),
            Paragraph(desc, td_desc_style),
        ]
        table_data.append([
            Paragraph(str(idx), td_center_style),
            item_cell,
            Paragraph(str(qty), td_right_style),
            Paragraph(unit, td_center_style),
            Paragraph(_format_currency(unit_price), td_right_style),
            Paragraph(_format_currency(total), td_right_style),
        ])

    items_table = Table(
        table_data,
        colWidths=[25, 245, 45, 45, 90, 90],
    )
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065F46")),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A7F3D0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0FDF4")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Totals block:
    # Printed Subtotal: $6,700.00 (2700 + 950 + 600 + 500 + 750 + 1200)
    # Grand Total: $6,700.00
    totals_data = [
        [Paragraph("Subtotal:", total_label_style), Paragraph(_format_currency(6700.00), total_val_style)],
        [Paragraph("Estimated Tax (0.0%):", total_label_style), Paragraph(_format_currency(0.00), total_val_style)],
        [Paragraph("Grand Total (USD):", total_label_style), Paragraph(_format_currency(6700.00), total_val_style)],
    ]
    totals_table = Table(totals_data, colWidths=[450, 90])
    totals_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEABOVE", (0, 2), (1, 2), 1, colors.HexColor("#065F46")),
        ])
    )
    story.append(KeepTogether([totals_table]))
    story.append(Spacer(1, 20))

    # Notes
    notes = [
        Paragraph("<b>Revision Notes & Conditions:</b>", td_name_style),
        Paragraph(
            "This revised quotation supercedes CST-2026-0891. Storage and compute tier allocations "
            "have been adjusted per engineering review meeting dated 2026-09-08.",
            td_desc_style,
        ),
        Spacer(1, 14),
        Paragraph("Authorized Provider Representative: <i>Marcus Vance, VP Enterprise Cloud Solutions</i>", td_desc_style),
    ]
    story.append(KeepTogether(notes))

    doc.build(story)


def build_offer_v1_reformatted(output_path: Path) -> None:
    """
    Generate offer_v1_reformatted.pdf: Exact same commercial data as offer_v1.pdf
    with completely different visual design, fonts, table border structure, and metadata layout.
    MUST result in EXACTLY 0 substantive commercial changes!
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Modern Minimalist Charcoal Styling
    title_style = ParagraphStyle(
        "Ref_Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#111827"),
    )
    meta_title_style = ParagraphStyle(
        "Ref_MetaTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6B7280"),
        alignment=2,
    )
    meta_desc_style = ParagraphStyle(
        "Ref_MetaDesc",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151"),
        alignment=2,
    )
    section_hdr_style = ParagraphStyle(
        "Ref_SecHdr",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    body_style = ParagraphStyle(
        "Ref_Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
    )
    th_style = ParagraphStyle(
        "Ref_TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#374151"),
        alignment=0,
    )
    th_right_style = ParagraphStyle(
        "Ref_THRight",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#374151"),
        alignment=2,
    )
    th_center_style = ParagraphStyle(
        "Ref_THCenter",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#374151"),
        alignment=1,
    )
    td_name_style = ParagraphStyle(
        "Ref_TDName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#111827"),
    )
    td_desc_style = ParagraphStyle(
        "Ref_TDDesc",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#6B7280"),
    )
    td_right_style = ParagraphStyle(
        "Ref_TDRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#111827"),
        alignment=2,
    )
    td_center_style = ParagraphStyle(
        "Ref_TDCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#111827"),
        alignment=1,
    )
    total_label_style = ParagraphStyle(
        "Ref_TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#374151"),
        alignment=2,
    )
    total_val_style = ParagraphStyle(
        "Ref_TotalVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
        alignment=2,
    )

    story = []

    # Two-column Header banner: Left Title, Right Metadata Block
    left_banner = [
        Paragraph("QUOTATION", title_style),
        Paragraph("CloudScale Technologies Enterprise Services", body_style),
    ]
    right_banner = [
        Paragraph("REFERENCE: <b>CST-2026-0891</b>", meta_title_style),
        Paragraph("ISSUE DATE: <b>2026-09-01</b>", meta_desc_style),
        Paragraph("TARGET DELIVERY: <b>2026-10-15</b>", meta_desc_style),
        Paragraph("CURRENCY: <b>USD</b> | TERMS: <b>Net 30</b>", meta_desc_style),
    ]
    top_table = Table([[left_banner, right_banner]], colWidths=[270, 270])
    top_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(top_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#111827"), spaceBefore=2, spaceAfter=14))

    # Parties Block (Vendor & Client in minimalist side-by-side columns)
    vendor_block = [
        Paragraph("SERVICE PROVIDER", section_hdr_style),
        Paragraph("CloudScale Technologies Inc.", body_style),
        Paragraph("100 Enterprise Way, Suite 400, San Francisco, CA 94105", body_style),
        Paragraph("sales@cloudscale-tech.example", body_style),
    ]
    client_block = [
        Paragraph("ISSUED TO", section_hdr_style),
        Paragraph("Acme Global Logistics LLC", body_style),
        Paragraph("742 Market Boulevard, Chicago, IL 60601", body_style),
        Paragraph("Procurement & Cloud Infrastructure Team", body_style),
    ]
    parties_table = Table([[vendor_block, client_block]], colWidths=[270, 270])
    parties_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ])
    )
    story.append(parties_table)
    story.append(Spacer(1, 14))

    # Items table (same 6 items and exact same values as offer_v1.pdf)
    table_data = [[
        Paragraph("NO.", th_center_style),
        Paragraph("DESCRIPTION OF GOODS & SERVICES", th_style),
        Paragraph("QTY", th_right_style),
        Paragraph("UNIT", th_center_style),
        Paragraph("RATE", th_right_style),
        Paragraph("AMOUNT", th_right_style),
    ]]

    v1_items = [
        (
            "01",
            "Dedicated Cloud Compute Node (c6i.4xlarge)",
            "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
            4,
            "nodes",
            450.00,
            1800.00,
        ),
        (
            "02",
            "Managed Kubernetes Control Plane",
            "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
            2,
            "clusters",
            300.00,
            600.00,
        ),
        (
            "03",
            "High-Performance NVMe Block Storage (5TB)",
            "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
            3,
            "volumes",
            250.00,
            750.00,
        ),
        (
            "04",
            "Multi-Region Cloud Load Balancer",
            "Layer 4/7 global traffic director with SSL offloading and automated health probing",
            2,
            "units",
            150.00,
            300.00,
        ),
        (
            "05",
            "Cloud Security & DDoS Shield Enterprise",
            "Automated WAF rulesets, volumetric DDoS mitigation, and intrusion prevention inspection",
            1,
            "license",
            850.00,
            850.00,
        ),
        (
            "06",
            "24/7 DevOps Support & SLA Package",
            "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
            1,
            "month",
            1200.00,
            1200.00,
        ),
    ]

    for idx_str, name, desc, qty, unit, unit_price, total in v1_items:
        item_cell = [
            Paragraph(name, td_name_style),
            Paragraph(desc, td_desc_style),
        ]
        table_data.append([
            Paragraph(idx_str, td_center_style),
            item_cell,
            Paragraph(str(qty), td_right_style),
            Paragraph(unit, td_center_style),
            Paragraph(_format_currency(unit_price), td_right_style),
            Paragraph(_format_currency(total), td_right_style),
        ])

    items_table = Table(
        table_data,
        colWidths=[30, 240, 40, 50, 90, 90],
    )
    items_table.setStyle(
        TableStyle([
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#111827")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Minimalist Totals
    totals_data = [
        [Paragraph("SUBTOTAL", total_label_style), Paragraph(_format_currency(5500.00), total_val_style)],
        [Paragraph("TAX (0%)", total_label_style), Paragraph(_format_currency(0.00), total_val_style)],
        [Paragraph("TOTAL DUE (USD)", total_label_style), Paragraph(_format_currency(5500.00), total_val_style)],
    ]
    totals_table = Table(totals_data, colWidths=[450, 90])
    totals_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEABOVE", (0, 2), (1, 2), 1, colors.HexColor("#111827")),
        ])
    )
    story.append(KeepTogether([totals_table]))
    story.append(Spacer(1, 18))

    # Notes
    footer_notes = [
        Paragraph("<b>Commercial Clarifications:</b>", section_hdr_style),
        Paragraph(
            "Pricing reflects agreed rate card CST-2026-0891 valid through 30 days from 2026-09-01. "
            "Governed by Master Services Agreement. Standard delivery scheduled for 2026-10-15.",
            body_style,
        ),
        Spacer(1, 10),
        Paragraph("Authorized Signatory: <i>Marcus Vance (VP Enterprise Cloud Solutions)</i>", body_style),
    ]
    story.append(KeepTogether(footer_notes))

    doc.build(story)


def build_offer_v2_ambiguous(output_path: Path) -> None:
    """
    Generate offer_v2_ambiguous.pdf: Revised offer where Item 5 has been replaced
    with a vague, ambiguously phrased product without an explicit SKU/part code:
    'Standard IT Infrastructure & Security Services - Tier Variable'.
    The AI system / semantic matcher MUST assign confidence=UNCERTAIN to this match.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Amb_Title",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#7C2D12"),  # Dark Amber/Rust
    )
    subtitle_style = ParagraphStyle(
        "Amb_Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
    )
    meta_label_style = ParagraphStyle(
        "Amb_MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#7C2D12"),
    )
    meta_val_style = ParagraphStyle(
        "Amb_MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
    )
    th_style = ParagraphStyle(
        "Amb_TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=0,
    )
    th_right_style = ParagraphStyle(
        "Amb_THRight",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=2,
    )
    th_center_style = ParagraphStyle(
        "Amb_THCenter",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1,
    )
    td_name_style = ParagraphStyle(
        "Amb_TDName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#111827"),
    )
    td_desc_style = ParagraphStyle(
        "Amb_TDDesc",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
    )
    td_right_style = ParagraphStyle(
        "Amb_TDRight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=2,
    )
    td_center_style = ParagraphStyle(
        "Amb_TDCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1F2937"),
        alignment=1,
    )
    total_label_style = ParagraphStyle(
        "Amb_TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#7C2D12"),
        alignment=2,
    )
    total_val_style = ParagraphStyle(
        "Amb_TotalVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#111827"),
        alignment=2,
    )

    story = []

    # Title
    story.append(Paragraph("COMMERCIAL PROPOSAL (AMENDMENT B)", title_style))
    story.append(Paragraph("Proposed Cloud Infrastructure & Security Services Scope", subtitle_style))
    story.append(Spacer(1, 14))

    # Metadata cards
    vendor_block = [
        Paragraph("<b>VENDOR / PROVIDER:</b>", meta_label_style),
        Paragraph("CloudScale Technologies Inc.", meta_val_style),
        Paragraph("100 Enterprise Way, Suite 400", meta_val_style),
        Paragraph("San Francisco, CA 94105", meta_val_style),
        Paragraph("Contact: sales@cloudscale-tech.example", meta_val_style),
    ]
    client_block = [
        Paragraph("<b>CLIENT / RECIPIENT:</b>", meta_label_style),
        Paragraph("Acme Global Logistics LLC", meta_val_style),
        Paragraph("742 Market Boulevard, Chicago, IL 60601", meta_val_style),
        Paragraph("Attn: Procurement & Cloud Infrastructure Team", meta_val_style),
    ]
    details_block = [
        Paragraph("<b>OFFER DETAILS:</b>", meta_label_style),
        Paragraph("Offer ID: <b>CST-2026-0891-AMB</b>", meta_val_style),
        Paragraph("Issue Date: <b>2026-09-05</b>", meta_val_style),
        Paragraph("Delivery Date: <b>2026-10-15</b>", meta_val_style),
        Paragraph("Currency: <b>USD ($)</b> | Terms: <b>Net 30</b>", meta_val_style),
    ]

    meta_table = Table(
        [[vendor_block, client_block, details_block]],
        colWidths=[175, 185, 180],
    )
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FDE68A")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # Items table header
    table_data = [[
        Paragraph("#", th_center_style),
        Paragraph("Line Item & Specification", th_style),
        Paragraph("Qty", th_right_style),
        Paragraph("Unit", th_center_style),
        Paragraph("Unit Price", th_right_style),
        Paragraph("Total Price", th_right_style),
    ]]

    # Items: items 1, 2, 3, 4, 6 match v1.
    # Item 5 is ambiguous: replaces 'Cloud Security & DDoS Shield Enterprise' ($850)
    # with 'Standard IT Infrastructure & Security Services - Tier Variable' ($800)
    # without a specific SKU.
    amb_items = [
        (
            1,
            "Dedicated Cloud Compute Node (c6i.4xlarge)",
            "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
            4,
            "nodes",
            450.00,
            1800.00,
        ),
        (
            2,
            "Managed Kubernetes Control Plane",
            "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
            2,
            "clusters",
            300.00,
            600.00,
        ),
        (
            3,
            "High-Performance NVMe Block Storage (5TB)",
            "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
            3,
            "volumes",
            250.00,
            750.00,
        ),
        (
            4,
            "Multi-Region Cloud Load Balancer",
            "Layer 4/7 global traffic director with SSL offloading and automated health probing",
            2,
            "units",
            150.00,
            300.00,
        ),
        (
            5,
            "Standard IT Infrastructure & Security Services - Tier Variable",
            "General cloud security maintenance, perimeter firewall inspection, or optional DDoS mitigation tier pending scope clarification",
            1,
            "pkg",
            800.00,
            800.00,
        ),
        (
            6,
            "24/7 DevOps Support & SLA Package",
            "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
            1,
            "month",
            1200.00,
            1200.00,
        ),
    ]

    for idx, name, desc, qty, unit, unit_price, total in amb_items:
        item_cell = [
            Paragraph(name, td_name_style),
            Paragraph(desc, td_desc_style),
        ]
        table_data.append([
            Paragraph(str(idx), td_center_style),
            item_cell,
            Paragraph(str(qty), td_right_style),
            Paragraph(unit, td_center_style),
            Paragraph(_format_currency(unit_price), td_right_style),
            Paragraph(_format_currency(total), td_right_style),
        ])

    items_table = Table(
        table_data,
        colWidths=[25, 245, 40, 50, 90, 90],
    )
    items_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C2D12")),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FED7AA")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFFBEB")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Totals block: 1800 + 600 + 750 + 300 + 800 + 1200 = 5450.00
    totals_data = [
        [Paragraph("Subtotal:", total_label_style), Paragraph(_format_currency(5450.00), total_val_style)],
        [Paragraph("Estimated Tax (0.0%):", total_label_style), Paragraph(_format_currency(0.00), total_val_style)],
        [Paragraph("Grand Total (USD):", total_label_style), Paragraph(_format_currency(5450.00), total_val_style)],
    ]
    totals_table = Table(totals_data, colWidths=[450, 90])
    totals_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LINEABOVE", (0, 2), (1, 2), 1, colors.HexColor("#7C2D12")),
        ])
    )
    story.append(KeepTogether([totals_table]))
    story.append(Spacer(1, 20))

    # Notes
    notes = [
        Paragraph("<b>Clarification Note:</b>", td_name_style),
        Paragraph(
            "Item 5 scope requires mutual confirmation prior to contract finalization. "
            "All pricing in USD. Valid for 30 calendar days.",
            td_desc_style,
        ),
        Spacer(1, 14),
        Paragraph("Authorized Provider Representative: <i>Marcus Vance, VP Enterprise Cloud Solutions</i>", td_desc_style),
    ]
    story.append(KeepTogether(notes))

    doc.build(story)


def generate_ground_truth(output_path: Path) -> dict[str, Any]:
    """
    Generate authoritative ground_truth.json containing structured specifications
    of expected changes and arithmetic audit outcomes for each test scenario.
    """
    ground_truth = {
        "metadata": {
            "version": "1.0",
            "description": "Authoritative ground truth for commercial offer comparison test scenarios",
            "currency": "USD",
            "max_pages_per_doc": 3,
        },
        "scenarios": {
            "scenario_1_substantive": {
                "scenario_id": "SCENARIO-1-SUBSTANTIVE",
                "title": "Main Commercial Pair: Substantive Changes, Reordering & Arithmetic Error",
                "baseline_document": "offer_v1.pdf",
                "revised_document": "offer_v2_substantive.pdf",
                "expected_substantive_changes_count": 7,
                "expected_header_changes": [
                    {
                        "field": "delivery_date",
                        "change_type": "DELIVERY_DATE_CHANGED",
                        "original_value": "2026-10-15",
                        "revised_value": "2026-11-01",
                        "confidence": "CONFIRMED",
                        "explanation": "Target delivery date extended from 2026-10-15 to 2026-11-01.",
                    },
                    {
                        "field": "grand_total",
                        "change_type": "TOTAL_CHANGED",
                        "original_value": 5500.00,
                        "revised_value": 6700.00,
                        "confidence": "CONFIRMED",
                        "explanation": "Grand total changed from $5,500.00 to $6,700.00 (+ $1,200.00).",
                    },
                ],
                "expected_line_item_changes": [
                    {
                        "change_type": "RENAMED",
                        "item_name_original": "Managed Kubernetes Control Plane",
                        "item_name_revised": "K8s Managed Control Plane & Orchestrator",
                        "original_value": {
                            "unit_price": 300.00,
                            "quantity": 2.0,
                            "total_price": 600.00,
                        },
                        "revised_value": {
                            "unit_price": 300.00,
                            "quantity": 2.0,
                            "total_price": 600.00,
                        },
                        "confidence": "CONFIRMED",
                        "explanation": "Renamed from 'Managed Kubernetes Control Plane' to 'K8s Managed Control Plane & Orchestrator' with identical quantities and pricing.",
                    },
                    {
                        "change_type": "QUANTITY_CHANGED",
                        "item_name_original": "Dedicated Cloud Compute Node (c6i.4xlarge)",
                        "item_name_revised": "Dedicated Cloud Compute Node (c6i.4xlarge)",
                        "original_value": 4.0,
                        "revised_value": 6.0,
                        "confidence": "CONFIRMED",
                        "explanation": "Quantity increased from 4 to 6 nodes, resulting in line total change from $1,800.00 to $2,700.00.",
                    },
                    {
                        "change_type": "UNIT_PRICE_CHANGED",
                        "item_name_original": "Cloud Security & DDoS Shield Enterprise",
                        "item_name_revised": "Cloud Security & DDoS Shield Enterprise",
                        "original_value": 850.00,
                        "revised_value": 950.00,
                        "confidence": "CONFIRMED",
                        "explanation": "Unit price increased from $850.00 to $950.00 per license.",
                    },
                    {
                        "change_type": "REMOVED",
                        "item_name_original": "Multi-Region Cloud Load Balancer",
                        "item_name_revised": None,
                        "original_value": {
                            "quantity": 2.0,
                            "unit_price": 150.00,
                            "total_price": 300.00,
                        },
                        "revised_value": None,
                        "confidence": "CONFIRMED",
                        "explanation": "Line item 'Multi-Region Cloud Load Balancer' was removed from revised offer.",
                    },
                    {
                        "change_type": "ADDED",
                        "item_name_original": None,
                        "item_name_revised": "Automated Disaster Recovery & Backup Replication",
                        "original_value": None,
                        "revised_value": {
                            "quantity": 1.0,
                            "unit_price": 500.00,
                            "total_price": 500.00,
                        },
                        "confidence": "CONFIRMED",
                        "explanation": "Newly added service 'Automated Disaster Recovery & Backup Replication' for $500.00.",
                    },
                ],
                "expected_reordering": {
                    "is_reordered": True,
                    "explanation": "Line items in revised document were reordered across positions 1 through 6.",
                },
                "expected_arithmetic_audit": {
                    "original_offer": {
                        "is_valid": True,
                        "discrepancies_count": 0,
                        "discrepancies": [],
                    },
                    "revised_offer": {
                        "is_valid": False,
                        "discrepancies_count": 1,
                        "discrepancies": [
                            {
                                "location": "Line item: 24/7 DevOps Support & SLA Package",
                                "expected_value": 1000.00,
                                "actual_value": 1200.00,
                                "message": "Calculation mismatch for '24/7 DevOps Support & SLA Package': expected 1000.00 (1.0 * 1000.00), but document states 1200.00",
                            }
                        ],
                    },
                },
            },
            "scenario_2_reformatted": {
                "scenario_id": "SCENARIO-2-REFORMATTED",
                "title": "Formatting-Only Variation: Layout & Typography Differences (Zero Commercial Changes)",
                "baseline_document": "offer_v1.pdf",
                "revised_document": "offer_v1_reformatted.pdf",
                "expected_substantive_changes_count": 0,
                "expected_changes": [],
                "expected_arithmetic_audit": {
                    "original_offer": {
                        "is_valid": True,
                        "discrepancies_count": 0,
                        "discrepancies": [],
                    },
                    "revised_offer": {
                        "is_valid": True,
                        "discrepancies_count": 0,
                        "discrepancies": [],
                    },
                },
                "notes": "Completely different visual styling, typography, table lines, and header positioning, but exactly identical commercial data. System must report 0 changes.",
            },
            "scenario_3_ambiguous": {
                "scenario_id": "SCENARIO-3-AMBIGUOUS",
                "title": "Ambiguity & Human Clarification: Unclear Item Scope Without Part Code",
                "baseline_document": "offer_v1.pdf",
                "revised_document": "offer_v2_ambiguous.pdf",
                "expected_uncertain_matches_count": 1,
                "expected_uncertain_matches": [
                    {
                        "item_name_original": "Cloud Security & DDoS Shield Enterprise",
                        "item_name_revised": "Standard IT Infrastructure & Security Services - Tier Variable",
                        "confidence": "UNCERTAIN",
                        "original_value": 850.00,
                        "revised_value": 800.00,
                        "explanation": "Item description is ambiguous and conflates general IT infrastructure with security scope without explicit SKU. Requires user review/clarification.",
                    }
                ],
                "expected_arithmetic_audit": {
                    "original_offer": {
                        "is_valid": True,
                        "discrepancies_count": 0,
                    },
                    "revised_offer": {
                        "is_valid": True,
                        "discrepancies_count": 0,
                    },
                },
            },
        },
    }

    output_path.write_text(json.dumps(ground_truth, indent=2, ensure_ascii=False), encoding="utf-8")
    return ground_truth


def verify_generated_pdfs(sample_files: list[Path]) -> None:
    """Verify that all generated PDFs exist, have <= 3 pages, and contain extractable text."""
    for pdf_path in sample_files:
        assert pdf_path.exists(), f"File {pdf_path.name} was not created!"
        with pdfplumber.open(str(pdf_path)) as pdf:
            num_pages = len(pdf.pages)
            assert 1 <= num_pages <= 3, f"{pdf_path.name} has {num_pages} pages, exceeding requirement (<= 3 pages)"
            full_text = " ".join((p.extract_text() or "") for p in pdf.pages).strip()
            assert len(full_text) > 100, f"{pdf_path.name} text extraction produced insufficient text!"
            assert "USD" in full_text or "$" in full_text, f"{pdf_path.name} missing currency indicator!"
            print(f"  [OK] {pdf_path.name:30} ({num_pages} page{'s' if num_pages > 1 else ''}, {len(full_text)} chars extracted)")


def main() -> None:
    """Generate all test PDF samples and ground truth metadata."""
    print("=" * 60)
    print("Generating Synthetic Commercial Offer PDF Suite...")
    print("=" * 60)

    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    files_to_generate = [
        (SAMPLES_DIR / "offer_v1.pdf", build_offer_v1),
        (SAMPLES_DIR / "offer_v2_substantive.pdf", build_offer_v2_substantive),
        (SAMPLES_DIR / "offer_v1_reformatted.pdf", build_offer_v1_reformatted),
        (SAMPLES_DIR / "offer_v2_ambiguous.pdf", build_offer_v2_ambiguous),
    ]

    for path, builder_fn in files_to_generate:
        print(f"Building {path.name}...")
        builder_fn(path)

    print("\nGenerating ground_truth.json...")
    generate_ground_truth(GROUND_TRUTH_PATH)
    print(f"  [OK] ground_truth.json ({GROUND_TRUTH_PATH.stat().st_size} bytes)")

    print("\nVerifying PDF extractions with pdfplumber:")
    verify_generated_pdfs([p for p, _ in files_to_generate])

    print("\n" + "=" * 60)
    print("All 4 synthetic PDFs and ground_truth.json successfully generated!")
    print(f"Output directory: {SAMPLES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

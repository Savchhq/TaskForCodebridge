"""
Prompts for AI-powered commercial offer data extraction and semantic item matching.
Enforces strict schema compliance, verbatim source snippet citations,
anti-arithmetic hallucination rules, and uncertainty quantification.
"""

from __future__ import annotations

import json
from app.models.schemas import LineItem, PageContent

EXTRACTION_SYSTEM_INSTRUCTION = """\
You are an expert commercial document parsing AI specialized in extracting structured data from commercial offers, proposals, and quotes.

Your objective is to extract the commercial metadata and line items from the provided document pages into the requested JSON schema.

CRITICAL EXTRACTION RULES:
1. STRICT ARITHMETIC INTEGRITY:
   - DO NOT CALCULATE OR RECALCULATE ANY NUMERICAL VALUES.
   - DO NOT multiply quantity by unit price.
   - DO NOT sum line item totals into grand totals.
   - Extract ONLY the literal, raw numbers printed in the document text.
   - If the document contains an arithmetic discrepancy (e.g. 1 unit at $1,000 listed with total $1,200), extract the exact printed value ($1,200). Never fix or alter printed numbers.

2. TRACEABILITY & SOURCE REFERENCES:
   - For every extracted line item, you MUST provide a `source_ref` object containing:
     * `page_number`: 1-indexed page number where the item appears.
     * `snippet`: an exact verbatim textual quote/excerpt from that page showing the line item.

3. LINE ITEMS EXTRACTION:
   - Extract all products, services, and line deliverables.
   - Capture `name`, `description`, `quantity`, `unit`, `unit_price`, and `total_price`.
   - Strip currency symbols from numeric price fields (e.g., "$1,200.00" -> 1200.0).

4. HEADER FIELDS:
   - `vendor_name`: The company or entity issuing the offer.
   - `client_name`: The client or recipient company.
   - `offer_id`: Proposal or quotation reference number.
   - `offer_date`: Issue or quote date (e.g. "YYYY-MM-DD" or as printed).
   - `delivery_date`: Target delivery date, timeline, or validity period.
   - `currency`: ISO code or currency identifier (e.g. "USD", "EUR", "GBP").
   - `subtotal`, `tax`, `grand_total`: Exact printed numerical amounts.
"""


MATCHING_SYSTEM_INSTRUCTION = """\
You are an expert commercial contract analyst comparing two versions of a commercial offer:
1. Original Offer
2. Revised Offer

Your task is to semantically match the line items between the Original and Revised offers.

CRITICAL MATCHING RULES:
1. SEMANTIC MATCHING ACROSS RENAMING & REORDERING:
   - Items may appear in a different row order; order differences are NOT commercial changes.
   - Items may be renamed or rephrased (e.g., "Managed Kubernetes Control Plane" vs "K8s Managed Control Plane & Orchestrator").
   - Compare item names, descriptions, technical specifications, and units to identify true equivalence.

2. CHANGE CATEGORIES & INDICES:
   - Use 0-indexed positions to reference items in the provided lists.
   - Matched Item: `original_index` is an integer AND `revised_index` is an integer.
   - Added Item: `original_index` is null, `revised_index` is an integer.
   - Removed Item: `original_index` is an integer, `revised_index` is null.

3. CONFIDENCE & UNCERTAINTY SCORING:
   - Assign a `confidence_score` between 0.0 and 1.0 for each item match.
   - If confidence_score >= 0.8: set `confidence_level` = "CONFIRMED".
   - If confidence_score < 0.8: set `confidence_level` = "UNCERTAIN".
   - Use "UNCERTAIN" when an item's scope is vague, lacks an explicit SKU/part number, or could represent a different service tier (e.g. "Standard IT Infrastructure & Security Services - Tier Variable" replacing a specific DDoS product).
   - For clearly added or removed items, confidence_score is 1.0 and confidence_level is "CONFIRMED".

4. RATIONALE:
   - Provide a concise explanation describing why items were paired, why confidence was docked if uncertain, or explaining additions/removals.
"""


def build_extraction_prompt(pages: list[PageContent]) -> str:
    """Format document pages into an extraction prompt."""
    sections: list[str] = []
    for page in pages:
        sections.append(
            f"=== PAGE {page.page_number} ===\n"
            f"{page.raw_text.strip()}\n"
        )
    pages_text = "\n".join(sections)

    return (
        "Please extract the commercial offer data from the following document pages.\n"
        "Remember: Extract literal printed numbers only; do not calculate or recalculate.\n\n"
        f"{pages_text}\n\n"
        "Return the extracted offer according to the OfferDocument JSON schema."
    )


def build_matching_prompt(
    original_items: list[LineItem],
    revised_items: list[LineItem],
) -> str:
    """Format original and revised line items into a matching prompt."""
    orig_list = []
    for idx, item in enumerate(original_items):
        orig_list.append({
            "index": idx,
            "name": item.name,
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        })

    rev_list = []
    for idx, item in enumerate(revised_items):
        rev_list.append({
            "index": idx,
            "name": item.name,
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        })

    prompt_dict = {
        "original_items": orig_list,
        "revised_items": rev_list,
    }

    return (
        "Please match the line items between Original Offer and Revised Offer.\n"
        "Account for reordered rows, renamed items, additions, and removals.\n\n"
        f"{json.dumps(prompt_dict, indent=2)}\n\n"
        "Return the matches as a JSON object matching the MatchResultRaw schema."
    )

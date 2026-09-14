"""
Mock AI Provider for deterministic offline testing without external API calls or token costs.
Emulates Gemini Flash extraction and semantic matching using ground truth benchmarks
and deterministic heuristic fallbacks.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Any

from app.models.schemas import (
    ConfidenceLevel,
    ItemMatch,
    LineItem,
    OfferDocument,
    PageContent,
    SourceReference,
)
from app.services.ai.base import BaseAIProvider
from app.services.pdf_extractor import find_source_snippet


class MockAIProvider(BaseAIProvider):
    """
    Deterministic AI provider for testing and development.
    Requires no API keys or internet connection.
    """

    # Pre-defined semantic aliases for benchmark scenarios
    KNOWN_MATCHES: dict[tuple[str, str], tuple[float, ConfidenceLevel, str]] = {
        (
            "managed kubernetes control plane",
            "k8s managed control plane & orchestrator",
        ): (
            0.95,
            ConfidenceLevel.CONFIRMED,
            "Renamed from 'Managed Kubernetes Control Plane' to 'K8s Managed Control Plane & Orchestrator' with matching specifications",
        ),
        (
            "cloud security & ddos shield enterprise",
            "standard it infrastructure & security services - tier variable",
        ): (
            0.65,
            ConfidenceLevel.UNCERTAIN,
            "Item description is ambiguous and conflates general IT infrastructure with security scope without explicit SKU. Requires user review/clarification.",
        ),
    }

    def __init__(self, ground_truth_path: Path | str | None = None) -> None:
        super().__init__()
        self.ground_truth_path = ground_truth_path
        self._ground_truth_data: dict[str, Any] | None = None
        self._load_ground_truth()

    def _load_ground_truth(self) -> None:
        """Attempt to load ground_truth.json from disk if present."""
        search_paths: list[Path] = []
        if self.ground_truth_path:
            search_paths.append(Path(self.ground_truth_path))

        # Default project paths
        current_file = Path(__file__).resolve()
        # backend/app/services/ai/mock_provider.py -> root is 4 levels up
        repo_root = current_file.parent.parent.parent.parent
        search_paths.append(repo_root / "test_fixtures" / "samples" / "ground_truth.json")

        for p in search_paths:
            if p.exists() and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        self._ground_truth_data = json.load(f)
                    break
                except Exception:
                    pass

    def extract_offer_data(self, pages: list[PageContent]) -> OfferDocument:
        """
        Extract structured commercial offer data from page contents.
        Matches benchmark document signatures (V1, V2 substantive, V2 ambiguous)
        or falls back to a deterministic text parser.
        """
        full_text = "\n".join(p.raw_text for p in pages)
        full_text_lower = full_text.lower()

        # Synthetic token usage recording
        prompt_tokens = max(120, sum(len(p.raw_text.split()) for p in pages) * 2)
        completion_tokens = 180
        self._record_usage(prompt_tokens, completion_tokens)

        # 1. Check for Scenario 1 Revised (offer_v2_substantive)
        if "cst-2026-0891-rev1" in full_text_lower or "revised commercial offer (rev-1)" in full_text_lower:
            return self._build_v2_substantive_doc(pages)

        # 2. Check for Scenario 3 Revised (offer_v2_ambiguous)
        if "cst-2026-0891-amb" in full_text_lower or "amendment b" in full_text_lower:
            return self._build_v2_ambiguous_doc(pages)

        # 3. Check for Scenario 1/2 Baseline or Reformatted (offer_v1 / offer_v1_reformatted)
        if "cst-2026-0891" in full_text_lower or "cloudscale technologies" in full_text_lower:
            return self._build_v1_baseline_doc(pages)

        # 4. Fallback deterministic heuristic extraction for generic test cases
        return self._build_fallback_doc(pages, full_text)

    def match_line_items(
        self,
        original_items: list[LineItem],
        revised_items: list[LineItem],
    ) -> list[ItemMatch]:
        """
        Match line items across original and revised offers.
        Emulates semantic LLM matching:
        - Exact matches (confidence 1.0, CONFIRMED).
        - Renamed / reordered items (confidence >= 0.8, CONFIRMED).
        - Ambiguous items (confidence < 0.8, UNCERTAIN).
        - Added items (original_item=None).
        - Removed items (revised_item=None).
        """
        # Synthetic token usage recording
        prompt_tokens = max(100, (len(original_items) + len(revised_items)) * 35)
        completion_tokens = max(80, (len(original_items) + len(revised_items)) * 25)
        self._record_usage(prompt_tokens, completion_tokens)

        matches: list[ItemMatch] = []
        unmatched_original = list(range(len(original_items)))
        unmatched_revised = list(range(len(revised_items)))

        # Pass 1: Exact name matching
        for r_idx in list(unmatched_revised):
            rev = revised_items[r_idx]
            rev_name_clean = rev.name.strip().lower()
            for o_idx in list(unmatched_original):
                orig = original_items[o_idx]
                orig_name_clean = orig.name.strip().lower()
                if rev_name_clean == orig_name_clean:
                    matches.append(
                        ItemMatch(
                            original_item=orig,
                            revised_item=rev,
                            confidence_score=1.0,
                            confidence_level=ConfidenceLevel.CONFIRMED,
                            rationale=f"Exact line item title match for '{orig.name}'",
                        )
                    )
                    unmatched_original.remove(o_idx)
                    unmatched_revised.remove(r_idx)
                    break

        # Pass 2: Known semantic aliases / ambiguous cases
        for r_idx in list(unmatched_revised):
            rev = revised_items[r_idx]
            rev_name_clean = rev.name.strip().lower()
            for o_idx in list(unmatched_original):
                orig = original_items[o_idx]
                orig_name_clean = orig.name.strip().lower()

                lookup_pair = (orig_name_clean, rev_name_clean)
                reverse_lookup = (rev_name_clean, orig_name_clean)

                if lookup_pair in self.KNOWN_MATCHES:
                    score, level, reason = self.KNOWN_MATCHES[lookup_pair]
                    matches.append(
                        ItemMatch(
                            original_item=orig,
                            revised_item=rev,
                            confidence_score=score,
                            confidence_level=level,
                            rationale=reason,
                        )
                    )
                    unmatched_original.remove(o_idx)
                    unmatched_revised.remove(r_idx)
                    break
                elif reverse_lookup in self.KNOWN_MATCHES:
                    score, level, reason = self.KNOWN_MATCHES[reverse_lookup]
                    matches.append(
                        ItemMatch(
                            original_item=orig,
                            revised_item=rev,
                            confidence_score=score,
                            confidence_level=level,
                            rationale=reason,
                        )
                    )
                    unmatched_original.remove(o_idx)
                    unmatched_revised.remove(r_idx)
                    break

        # Pass 3: Fuzzy / SequenceMatcher similarity for general test items
        for r_idx in list(unmatched_revised):
            rev = revised_items[r_idx]
            best_match_idx: int | None = None
            best_score = 0.0

            for o_idx in unmatched_original:
                orig = original_items[o_idx]
                ratio = difflib.SequenceMatcher(
                    None,
                    orig.name.strip().lower(),
                    rev.name.strip().lower(),
                ).ratio()
                if ratio > best_score:
                    best_score = ratio
                    best_match_idx = o_idx

            if best_match_idx is not None and best_score >= 0.4:
                orig = original_items[best_match_idx]
                conf_level = (
                    ConfidenceLevel.CONFIRMED
                    if best_score >= 0.8
                    else ConfidenceLevel.UNCERTAIN
                )
                rationale = (
                    f"Semantic similarity match ({best_score:.2f}) between '{orig.name}' and '{rev.name}'"
                    if conf_level == ConfidenceLevel.CONFIRMED
                    else f"Partial/ambiguous similarity ({best_score:.2f}) between '{orig.name}' and '{rev.name}', flagged for manual review"
                )
                matches.append(
                    ItemMatch(
                        original_item=orig,
                        revised_item=rev,
                        confidence_score=round(best_score, 2),
                        confidence_level=conf_level,
                        rationale=rationale,
                    )
                )
                unmatched_original.remove(best_match_idx)
                unmatched_revised.remove(r_idx)

        # Pass 4: Remaining revised items are ADDED
        for r_idx in unmatched_revised:
            rev = revised_items[r_idx]
            matches.append(
                ItemMatch(
                    original_item=None,
                    revised_item=rev,
                    confidence_score=1.0,
                    confidence_level=ConfidenceLevel.CONFIRMED,
                    rationale=f"Newly added service '{rev.name}'",
                )
            )

        # Pass 5: Remaining original items are REMOVED
        for o_idx in unmatched_original:
            orig = original_items[o_idx]
            matches.append(
                ItemMatch(
                    original_item=orig,
                    revised_item=None,
                    confidence_score=1.0,
                    confidence_level=ConfidenceLevel.CONFIRMED,
                    rationale=f"Line item '{orig.name}' was removed from revised offer",
                )
            )

        return matches

    def _build_v1_baseline_doc(self, pages: list[PageContent]) -> OfferDocument:
        """Build OfferDocument for offer_v1.pdf baseline."""
        raw_items = [
            (
                "Dedicated Cloud Compute Node (c6i.4xlarge)",
                "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
                4.0,
                "nodes",
                450.0,
                1800.0,
            ),
            (
                "Managed Kubernetes Control Plane",
                "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
                2.0,
                "clusters",
                300.0,
                600.0,
            ),
            (
                "High-Performance NVMe Block Storage (5TB)",
                "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
                3.0,
                "volumes",
                250.0,
                750.0,
            ),
            (
                "Multi-Region Cloud Load Balancer",
                "Layer 4/7 global traffic director with SSL offloading and automated health probing",
                2.0,
                "units",
                150.0,
                300.0,
            ),
            (
                "Cloud Security & DDoS Shield Enterprise",
                "Automated WAF rulesets, volumetric DDoS mitigation, and intrusion prevention inspection",
                1.0,
                "license",
                850.0,
                850.0,
            ),
            (
                "24/7 DevOps Support & SLA Package",
                "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
                1.0,
                "month",
                1200.0,
                1200.0,
            ),
        ]

        items = []
        for idx, (name, desc, qty, unit, unit_p, total_p) in enumerate(raw_items, start=1):
            ref = find_source_snippet(pages, name) or SourceReference(
                page_number=1, snippet=f"{idx} {name} {qty} {unit} ${unit_p:,.2f} ${total_p:,.2f}"
            )
            items.append(
                LineItem(
                    item_id=str(idx),
                    name=name,
                    description=desc,
                    quantity=qty,
                    unit=unit,
                    unit_price=unit_p,
                    total_price=total_p,
                    source_ref=ref,
                )
            )

        return OfferDocument(
            vendor_name="CloudScale Technologies Inc.",
            client_name="Acme Global Logistics LLC",
            offer_id="CST-2026-0891",
            offer_date="2026-09-01",
            delivery_date="2026-10-15",
            currency="USD",
            items=items,
            subtotal=5500.0,
            tax=0.0,
            grand_total=5500.0,
        )

    def _build_v2_substantive_doc(self, pages: list[PageContent]) -> OfferDocument:
        """
        Build OfferDocument for offer_v2_substantive.pdf.
        Note: Preserves deliberate arithmetic discrepancy on 24/7 DevOps Support
        where unit price $1,000 * 1 qty is printed as $1,200.00!
        """
        raw_items = [
            (
                "Dedicated Cloud Compute Node (c6i.4xlarge)",
                "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
                6.0,
                "nodes",
                450.0,
                2700.0,
            ),
            (
                "Cloud Security & DDoS Shield Enterprise",
                "Automated WAF rulesets, volumetric DDoS mitigation, and intrusion prevention inspection",
                1.0,
                "license",
                950.0,
                950.0,
            ),
            (
                "K8s Managed Control Plane & Orchestrator",
                "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
                2.0,
                "clusters",
                300.0,
                600.0,
            ),
            (
                "Automated Disaster Recovery & Backup Replication",
                "Cross-region continuous data replication with 15-minute RPO and 1-hour RTO",
                1.0,
                "service",
                500.0,
                500.0,
            ),
            (
                "High-Performance NVMe Block Storage (5TB)",
                "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
                3.0,
                "volumes",
                250.0,
                750.0,
            ),
            (
                "24/7 DevOps Support & SLA Package",
                "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
                1.0,
                "month",
                1000.0,
                1200.0,  # DELIBERATE SOURCE MATH ERROR: 1 * 1000 != 1200!
            ),
        ]

        items = []
        for idx, (name, desc, qty, unit, unit_p, total_p) in enumerate(raw_items, start=1):
            ref = find_source_snippet(pages, name) or SourceReference(
                page_number=1, snippet=f"{idx} {name} {qty} {unit} ${unit_p:,.2f} ${total_p:,.2f}"
            )
            items.append(
                LineItem(
                    item_id=str(idx),
                    name=name,
                    description=desc,
                    quantity=qty,
                    unit=unit,
                    unit_price=unit_p,
                    total_price=total_p,
                    source_ref=ref,
                )
            )

        return OfferDocument(
            vendor_name="CloudScale Technologies Inc.",
            client_name="Acme Global Logistics LLC",
            offer_id="CST-2026-0891-REV1",
            offer_date="2026-09-10",
            delivery_date="2026-11-01",
            currency="USD",
            items=items,
            subtotal=6700.0,
            tax=0.0,
            grand_total=6700.0,
        )

    def _build_v2_ambiguous_doc(self, pages: list[PageContent]) -> OfferDocument:
        """Build OfferDocument for offer_v2_ambiguous.pdf."""
        raw_items = [
            (
                "Dedicated Cloud Compute Node (c6i.4xlarge)",
                "High performance 16 vCPU, 64GB RAM compute instance with dedicated hypervisor tenancy",
                4.0,
                "nodes",
                450.0,
                1800.0,
            ),
            (
                "Managed Kubernetes Control Plane",
                "Multi-AZ high-availability K8s master nodes with automated backup and monitoring",
                2.0,
                "clusters",
                300.0,
                600.0,
            ),
            (
                "High-Performance NVMe Block Storage (5TB)",
                "Provisioned IOPS block volumes with 99.999% data durability and automated snapshotting",
                3.0,
                "volumes",
                250.0,
                750.0,
            ),
            (
                "Multi-Region Cloud Load Balancer",
                "Layer 4/7 global traffic director with SSL offloading and automated health probing",
                2.0,
                "units",
                150.0,
                300.0,
            ),
            (
                "Standard IT Infrastructure & Security Services - Tier Variable",
                "General cloud security maintenance, perimeter firewall inspection, or optional DDoS mitigation tier pending scope clarification",
                1.0,
                "pkg",
                800.0,
                800.0,
            ),
            (
                "24/7 DevOps Support & SLA Package",
                "Dedicated enterprise TAM, guaranteed 15-minute response SLA, and architecture review",
                1.0,
                "month",
                1200.0,
                1200.0,
            ),
        ]

        items = []
        for idx, (name, desc, qty, unit, unit_p, total_p) in enumerate(raw_items, start=1):
            ref = find_source_snippet(pages, name) or SourceReference(
                page_number=1, snippet=f"{idx} {name} {qty} {unit} ${unit_p:,.2f} ${total_p:,.2f}"
            )
            items.append(
                LineItem(
                    item_id=str(idx),
                    name=name,
                    description=desc,
                    quantity=qty,
                    unit=unit,
                    unit_price=unit_p,
                    total_price=total_p,
                    source_ref=ref,
                )
            )

        return OfferDocument(
            vendor_name="CloudScale Technologies Inc.",
            client_name="Acme Global Logistics LLC",
            offer_id="CST-2026-0891-AMB",
            offer_date="2026-09-05",
            delivery_date="2026-10-15",
            currency="USD",
            items=items,
            subtotal=5450.0,
            tax=0.0,
            grand_total=5450.0,
        )

    def _build_fallback_doc(self, pages: list[PageContent], full_text: str) -> OfferDocument:
        """
        Deterministic heuristic extraction fallback for any arbitrary PDF pages.
        Extracts headers and line items from text patterns.
        """
        vendor_match = re.search(r"(?:vendor|provider|from):\s*([^\n]+)", full_text, re.IGNORECASE)
        client_match = re.search(r"(?:client|customer|recipient|to):\s*([^\n]+)", full_text, re.IGNORECASE)
        offer_id_match = re.search(r"(?:offer\s*id|quote\s*#?|proposal\s*#?):\s*([^\s\n]+)", full_text, re.IGNORECASE)
        date_match = re.search(r"(?:date|issue\s*date):\s*(\d{4}-\d{2}-\d{2})", full_text, re.IGNORECASE)
        delivery_match = re.search(r"(?:delivery\s*date|target\s*delivery):\s*(\d{4}-\d{2}-\d{2})", full_text, re.IGNORECASE)
        total_match = re.search(r"(?:grand\s*total|total\s*amount)[\s\:\$]*([\d,\.]+)", full_text, re.IGNORECASE)

        grand_total = None
        if total_match:
            try:
                grand_total = float(total_match.group(1).replace(",", ""))
            except ValueError:
                pass

        items: list[LineItem] = []
        item_counter = 1

        for page in pages:
            for line in page.lines:
                # Look for lines with prices and numbers: Name ... $X ... $Y
                price_matches = re.findall(r"\$?\s*([\d,]+\.\d{2})", line)
                if len(price_matches) >= 2:
                    unit_p = float(price_matches[-2].replace(",", ""))
                    tot_p = float(price_matches[-1].replace(",", ""))
                    name_part = line.split("$")[0].strip() or f"Line Item {item_counter}"
                    # Clean leading numbers/index
                    name_clean = re.sub(r"^\d+[\.\)\s]+", "", name_part).strip() or name_part

                    items.append(
                        LineItem(
                            item_id=str(item_counter),
                            name=name_clean,
                            quantity=1.0,
                            unit="unit",
                            unit_price=unit_p,
                            total_price=tot_p,
                            source_ref=SourceReference(
                                page_number=page.page_number,
                                snippet=line,
                            ),
                        )
                    )
                    item_counter += 1

        return OfferDocument(
            vendor_name=vendor_match.group(1).strip() if vendor_match else "Commercial Vendor",
            client_name=client_match.group(1).strip() if client_match else "Client Recipient",
            offer_id=offer_id_match.group(1).strip() if offer_id_match else "OFFER-001",
            offer_date=date_match.group(1).strip() if date_match else "2026-09-01",
            delivery_date=delivery_match.group(1).strip() if delivery_match else "2026-10-15",
            currency="USD",
            items=items,
            subtotal=grand_total,
            tax=0.0,
            grand_total=grand_total or (sum(it.total_price for it in items if it.total_price) if items else 0.0),
        )

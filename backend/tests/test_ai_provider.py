"""
Unit tests for AI extraction and semantic matching pipeline.
Tests MockAIProvider, GeminiFlashProvider initialization and execution,
token cost calculations, semantic matching rules, uncertainty scoring,
and arithmetic integrity preservation.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from app.models.schemas import (
    ConfidenceLevel,
    ItemMatch,
    LineItem,
    OfferDocument,
    PageContent,
    SourceReference,
    TokenUsage,
)
from app.services.ai import (
    BaseAIProvider,
    GeminiFlashProvider,
    MockAIProvider,
    calculate_gemini_cost,
    get_ai_provider,
)
from app.services.ai.gemini_provider import RawItemMatch, RawMatchResponse
from app.services.ai.prompts import (
    EXTRACTION_SYSTEM_INSTRUCTION,
    MATCHING_SYSTEM_INSTRUCTION,
    build_extraction_prompt,
    build_matching_prompt,
)
from app.services.pdf_extractor import extract_pdf_pages

# Fixture paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = REPO_ROOT / "test_fixtures" / "samples"
OFFER_V1_PATH = SAMPLES_DIR / "offer_v1.pdf"
OFFER_V2_SUB_PATH = SAMPLES_DIR / "offer_v2_substantive.pdf"
OFFER_V1_REF_PATH = SAMPLES_DIR / "offer_v1_reformatted.pdf"
OFFER_V2_AMB_PATH = SAMPLES_DIR / "offer_v2_ambiguous.pdf"


@pytest.fixture
def mock_provider() -> MockAIProvider:
    return MockAIProvider()


# =========================================================================
# 1. Cost & Base Provider Tests
# =========================================================================

def test_calculate_gemini_cost():
    """Verify pricing math based on $0.075 / 1M input, $0.30 / 1M output."""
    # 1,000,000 prompt tokens = $0.075
    cost_prompt = calculate_gemini_cost(1_000_000, 0)
    assert cost_prompt == 0.075

    # 1,000,000 completion tokens = $0.30
    cost_comp = calculate_gemini_cost(0, 1_000_000)
    assert cost_comp == 0.30

    # 10,000 prompt + 2,000 completion
    # (10,000 * 0.075 / 1M) + (2,000 * 0.30 / 1M) = 0.00075 + 0.0006 = 0.00135
    cost_mixed = calculate_gemini_cost(10_000, 2_000)
    assert cost_mixed == 0.00135


def test_token_usage_lifecycle(mock_provider: MockAIProvider):
    """Verify session token accumulation and resetting."""
    assert mock_provider.last_token_usage.total_tokens == 0
    assert mock_provider.cumulative_token_usage.total_tokens == 0

    pages = [PageContent(page_number=1, raw_text="CloudScale Technologies CST-2026-0891 Total: $5,500.00")]
    mock_provider.extract_offer_data(pages)

    first_last = mock_provider.last_token_usage
    assert first_last.total_tokens > 0
    assert first_last.estimated_cost_usd >= 0.0
    assert mock_provider.cumulative_token_usage.total_tokens == first_last.total_tokens

    # Second invocation accumulates
    mock_provider.extract_offer_data(pages)
    assert mock_provider.cumulative_token_usage.total_tokens == first_last.total_tokens * 2

    # Reset
    mock_provider.reset_token_usage()
    assert mock_provider.last_token_usage.total_tokens == 0
    assert mock_provider.cumulative_token_usage.total_tokens == 0


# =========================================================================
# 2. MockAIProvider Extraction Tests on Benchmark PDFs
# =========================================================================

def test_mock_extraction_offer_v1(mock_provider: MockAIProvider):
    """Test extraction of baseline offer_v1.pdf."""
    assert OFFER_V1_PATH.exists(), f"Missing fixture: {OFFER_V1_PATH}"
    pages = extract_pdf_pages(OFFER_V1_PATH.read_bytes())

    doc = mock_provider.extract_offer_data(pages)

    assert doc.offer_id == "CST-2026-0891"
    assert doc.vendor_name == "CloudScale Technologies Inc."
    assert doc.client_name == "Acme Global Logistics LLC"
    assert doc.delivery_date == "2026-10-15"
    assert doc.currency == "USD"
    assert doc.grand_total == 5500.0
    assert len(doc.items) == 6

    # Verify every line item has a valid source reference
    for item in doc.items:
        assert item.source_ref is not None
        assert item.source_ref.page_number >= 1
        assert len(item.source_ref.snippet) > 0


def test_mock_extraction_offer_v2_substantive_math_integrity(mock_provider: MockAIProvider):
    """
    Test extraction of revised offer_v2_substantive.pdf.
    CRITICAL: Verifies that the AI does NOT recalculate arithmetic discrepancies
    and preserves 24/7 DevOps Support total as $1,200.00 (while 1 * 1000 = 1000).
    """
    assert OFFER_V2_SUB_PATH.exists()
    pages = extract_pdf_pages(OFFER_V2_SUB_PATH.read_bytes())

    doc = mock_provider.extract_offer_data(pages)

    assert doc.offer_id == "CST-2026-0891-REV1"
    assert doc.delivery_date == "2026-11-01"
    assert doc.grand_total == 6700.0
    assert len(doc.items) == 6

    # Find the deliberate math error line item
    devops_item = next((it for it in doc.items if "DevOps Support" in it.name), None)
    assert devops_item is not None
    assert devops_item.quantity == 1.0
    assert devops_item.unit_price == 1000.0
    # Must be 1200.0 as printed on the PDF, NOT 1000.0!
    assert devops_item.total_price == 1200.0


def test_mock_extraction_offer_v1_reformatted(mock_provider: MockAIProvider):
    """Test extraction of reformatted offer_v1."""
    assert OFFER_V1_REF_PATH.exists()
    pages = extract_pdf_pages(OFFER_V1_REF_PATH.read_bytes())

    doc = mock_provider.extract_offer_data(pages)
    assert doc.offer_id == "CST-2026-0891"
    assert doc.grand_total == 5500.0
    assert len(doc.items) == 6


def test_mock_extraction_offer_v2_ambiguous(mock_provider: MockAIProvider):
    """Test extraction of ambiguous offer_v2."""
    assert OFFER_V2_AMB_PATH.exists()
    pages = extract_pdf_pages(OFFER_V2_AMB_PATH.read_bytes())

    doc = mock_provider.extract_offer_data(pages)
    assert doc.offer_id == "CST-2026-0891-AMB"
    assert len(doc.items) == 6
    amb_item = next((it for it in doc.items if "Tier Variable" in it.name), None)
    assert amb_item is not None
    assert amb_item.total_price == 800.0


def test_mock_extraction_fallback_arbitrary_doc(mock_provider: MockAIProvider):
    """Test heuristic fallback extraction for custom arbitrary text."""
    pages = [
        PageContent(
            page_number=1,
            raw_text="Vendor: Alpha Tech\nClient: Beta Corp\nOffer ID: PROPOSAL-999\nDate: 2026-05-01\nDelivery Date: 2026-06-01\n1. Custom Widget A  $100.00  $200.00\nGrand Total: $200.00",
            lines=[
                "Vendor: Alpha Tech",
                "Client: Beta Corp",
                "Offer ID: PROPOSAL-999",
                "Date: 2026-05-01",
                "Delivery Date: 2026-06-01",
                "1. Custom Widget A  $100.00  $200.00",
                "Grand Total: $200.00",
            ],
        )
    ]

    doc = mock_provider.extract_offer_data(pages)
    assert doc.vendor_name == "Alpha Tech"
    assert doc.client_name == "Beta Corp"
    assert doc.offer_id == "PROPOSAL-999"
    assert len(doc.items) == 1
    assert doc.items[0].unit_price == 100.0
    assert doc.items[0].total_price == 200.0
    assert doc.items[0].source_ref is not None


# =========================================================================
# 3. MockAIProvider Semantic Matching Tests
# =========================================================================

def test_mock_matching_scenario_1_substantive(mock_provider: MockAIProvider):
    """
    Test semantic matching on Scenario 1:
    - 1 Renamed item: 'Managed Kubernetes Control Plane' -> 'K8s Managed Control Plane & Orchestrator'
    - 1 Removed item: 'Multi-Region Cloud Load Balancer'
    - 1 Added item: 'Automated Disaster Recovery & Backup Replication'
    - Reordered rows matched properly
    - High confidence (CONFIRMED) for valid matches.
    """
    v1_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V1_PATH.read_bytes()))
    v2_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V2_SUB_PATH.read_bytes()))

    matches = mock_provider.match_line_items(v1_doc.items, v2_doc.items)

    # 5 matched items (4 unchanged + 1 renamed) + 1 added + 1 removed = 7 total match decisions
    assert len(matches) == 7

    # 1. Renamed item
    renamed_match = next(
        (
            m
            for m in matches
            if m.original_item
            and m.original_item.name == "Managed Kubernetes Control Plane"
        ),
        None,
    )
    assert renamed_match is not None
    assert renamed_match.revised_item is not None
    assert renamed_match.revised_item.name == "K8s Managed Control Plane & Orchestrator"
    assert renamed_match.confidence_score >= 0.8
    assert renamed_match.confidence_level == ConfidenceLevel.CONFIRMED
    assert "Renamed from" in (renamed_match.rationale or "")

    # 2. Removed item
    removed_match = next(
        (
            m
            for m in matches
            if m.original_item
            and m.original_item.name == "Multi-Region Cloud Load Balancer"
        ),
        None,
    )
    assert removed_match is not None
    assert removed_match.revised_item is None
    assert removed_match.confidence_level == ConfidenceLevel.CONFIRMED
    assert "removed" in (removed_match.rationale or "").lower()

    # 3. Added item
    added_match = next(
        (
            m
            for m in matches
            if m.revised_item
            and m.revised_item.name == "Automated Disaster Recovery & Backup Replication"
        ),
        None,
    )
    assert added_match is not None
    assert added_match.original_item is None
    assert added_match.confidence_level == ConfidenceLevel.CONFIRMED
    assert "added" in (added_match.rationale or "").lower()

    # 4. Modified items (reordered but matched)
    compute_match = next(
        (
            m
            for m in matches
            if m.original_item
            and "Dedicated Cloud Compute Node" in m.original_item.name
        ),
        None,
    )
    assert compute_match is not None
    assert compute_match.revised_item is not None
    assert compute_match.confidence_score == 1.0
    assert compute_match.confidence_level == ConfidenceLevel.CONFIRMED


def test_mock_matching_scenario_2_reformatted(mock_provider: MockAIProvider):
    """
    Test matching on formatting-only variation (offer_v1 vs offer_v1_reformatted):
    All 6 items should match 100% with confidence 1.0 and CONFIRMED.
    """
    v1_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V1_PATH.read_bytes()))
    v1_ref_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V1_REF_PATH.read_bytes()))

    matches = mock_provider.match_line_items(v1_doc.items, v1_ref_doc.items)
    assert len(matches) == 6

    for m in matches:
        assert m.original_item is not None
        assert m.revised_item is not None
        assert m.confidence_score == 1.0
        assert m.confidence_level == ConfidenceLevel.CONFIRMED


def test_mock_matching_scenario_3_ambiguous_uncertainty(mock_provider: MockAIProvider):
    """
    Test matching on ambiguous revision (offer_v1 vs offer_v2_ambiguous):
    The ambiguous item without SKU must be classified as UNCERTAIN (< 0.8).
    """
    v1_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V1_PATH.read_bytes()))
    v2_amb_doc = mock_provider.extract_offer_data(extract_pdf_pages(OFFER_V2_AMB_PATH.read_bytes()))

    matches = mock_provider.match_line_items(v1_doc.items, v2_amb_doc.items)

    uncertain_match = next(
        (
            m
            for m in matches
            if m.revised_item
            and "Tier Variable" in m.revised_item.name
        ),
        None,
    )
    assert uncertain_match is not None
    assert uncertain_match.original_item is not None
    assert uncertain_match.original_item.name == "Cloud Security & DDoS Shield Enterprise"
    assert uncertain_match.confidence_score < 0.8
    assert uncertain_match.confidence_level == ConfidenceLevel.UNCERTAIN
    assert "ambiguous" in (uncertain_match.rationale or "").lower()


def test_mock_matching_generic_similarity(mock_provider: MockAIProvider):
    """Test general fuzzy matching logic for arbitrary line items."""
    orig_items = [
        LineItem(name="Enterprise Server License (Gold Edition)", unit_price=500.0),
        LineItem(name="Standard Storage Volume 1TB", unit_price=50.0),
    ]
    rev_items = [
        # Highly similar
        LineItem(name="Enterprise Server License - Gold Edition", unit_price=550.0),
        # New item
        LineItem(name="High Speed Networking Interface", unit_price=200.0),
    ]

    matches = mock_provider.match_line_items(orig_items, rev_items)
    assert len(matches) == 3  # 1 matched, 1 removed, 1 added

    matched = next((m for m in matches if m.original_item and m.revised_item), None)
    assert matched is not None
    assert matched.confidence_score >= 0.8
    assert matched.confidence_level == ConfidenceLevel.CONFIRMED


# =========================================================================
# 4. GeminiFlashProvider Initialization & Mocked API Tests
# =========================================================================

def test_gemini_provider_init():
    """Verify GeminiFlashProvider initialization and settings fallback."""
    provider = GeminiFlashProvider(api_key="test_key", model="gemini-2.5-flash")
    assert provider.api_key == "test_key"
    assert provider.model == "gemini-2.5-flash"
    assert provider.client is not None


def test_gemini_provider_missing_api_key():
    """Verify ValueError when calling Gemini provider without API key."""
    provider = GeminiFlashProvider(api_key="")
    provider.client = None

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        provider.extract_offer_data([PageContent(page_number=1, raw_text="text")])

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        provider.match_line_items([], [])


def test_gemini_provider_extract_mocked():
    """Verify GeminiFlashProvider extraction flow with mocked SDK response."""
    provider = GeminiFlashProvider(api_key="mock_key")

    mock_response = MagicMock()
    mock_response.text = (
        '{"vendor_name": "Acme Cloud", "offer_id": "OFF-123", "grand_total": 1000.0, '
        '"items": [{"name": "Compute", "quantity": 1.0, "unit_price": 1000.0, "total_price": 1000.0}]}'
    )
    mock_usage = MagicMock()
    mock_usage.prompt_token_count = 250
    mock_usage.candidates_token_count = 100
    mock_response.usage_metadata = mock_usage

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    provider.client = mock_client

    pages = [PageContent(page_number=1, raw_text="Acme Cloud OFF-123 Compute $1000.00", lines=["Compute $1000.00"])]
    doc = provider.extract_offer_data(pages)

    assert doc.vendor_name == "Acme Cloud"
    assert doc.offer_id == "OFF-123"
    assert doc.grand_total == 1000.0
    assert len(doc.items) == 1
    assert doc.items[0].source_ref is not None  # enriched from pages
    assert provider.last_token_usage.prompt_tokens == 250
    assert provider.last_token_usage.completion_tokens == 100
    assert provider.last_token_usage.total_tokens == 350
    assert provider.last_token_usage.estimated_cost_usd > 0


def test_gemini_provider_matching_mocked():
    """Verify GeminiFlashProvider matching flow with mocked SDK response."""
    provider = GeminiFlashProvider(api_key="mock_key")

    mock_response = MagicMock()
    mock_response.text = (
        '{"matches": ['
        '  {"original_index": 0, "revised_index": 0, "confidence_score": 0.95, "confidence_level": "CONFIRMED", "rationale": "Same item"},'
        '  {"original_index": 1, "revised_index": 1, "confidence_score": 0.60, "confidence_level": "UNCERTAIN", "rationale": "Ambiguous scope"}'
        ']}'
    )
    mock_usage = MagicMock()
    mock_usage.prompt_token_count = 300
    mock_usage.candidates_token_count = 80
    mock_response.usage_metadata = mock_usage

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    provider.client = mock_client

    orig = [
        LineItem(name="Item A", total_price=100.0),
        LineItem(name="Item B", total_price=200.0),
    ]
    rev = [
        LineItem(name="Item A v2", total_price=100.0),
        LineItem(name="Vague IT Services", total_price=180.0),
    ]

    matches = provider.match_line_items(orig, rev)
    assert len(matches) == 2

    assert matches[0].confidence_level == ConfidenceLevel.CONFIRMED
    assert matches[0].confidence_score == 0.95

    assert matches[1].confidence_level == ConfidenceLevel.UNCERTAIN
    assert matches[1].confidence_score == 0.60
    assert provider.last_token_usage.total_tokens == 380


# =========================================================================
# 5. Factory Function Tests
# =========================================================================

def test_get_ai_provider_factory():
    """Verify get_ai_provider factory for mock, gemini, and auto."""
    mock_p = get_ai_provider("mock")
    assert isinstance(mock_p, MockAIProvider)

    gemini_p = get_ai_provider("gemini")
    assert isinstance(gemini_p, GeminiFlashProvider)

    auto_p = get_ai_provider("auto")
    assert isinstance(auto_p, BaseAIProvider)

    with pytest.raises(ValueError, match="Unknown AI provider type"):
        get_ai_provider("invalid_provider")


# =========================================================================
# 6. Prompts Tests
# =========================================================================

def test_prompts_rules_and_structure():
    """Verify prompts enforce anti-hallucination and source citation rules."""
    assert "DO NOT CALCULATE OR RECALCULATE" in EXTRACTION_SYSTEM_INSTRUCTION
    assert "source_ref" in EXTRACTION_SYSTEM_INSTRUCTION
    assert "CONFIRMED" in MATCHING_SYSTEM_INSTRUCTION
    assert "UNCERTAIN" in MATCHING_SYSTEM_INSTRUCTION

    pages = [PageContent(page_number=1, raw_text="Sample raw text", lines=["Sample raw text"])]
    ext_prompt = build_extraction_prompt(pages)
    assert "PAGE 1" in ext_prompt
    assert "Sample raw text" in ext_prompt

    items = [LineItem(name="Widget", quantity=2.0, unit_price=10.0, total_price=20.0)]
    match_prompt = build_matching_prompt(items, items)
    assert "Widget" in match_prompt
    assert "original_items" in match_prompt
    assert "revised_items" in match_prompt


def test_matching_empty_lists(mock_provider: MockAIProvider):
    """Verify matching with empty lists returns empty matches."""
    matches = mock_provider.match_line_items([], [])
    assert matches == []


def test_matching_only_added_items(mock_provider: MockAIProvider):
    """Verify that when original has no items, all revised items are added."""
    rev = [
        LineItem(name="Item 1", total_price=100.0),
        LineItem(name="Item 2", total_price=200.0),
    ]
    matches = mock_provider.match_line_items([], rev)
    assert len(matches) == 2
    for m in matches:
        assert m.original_item is None
        assert m.revised_item is not None
        assert m.confidence_score == 1.0
        assert m.confidence_level == ConfidenceLevel.CONFIRMED
        assert "added" in (m.rationale or "").lower()


def test_matching_only_removed_items(mock_provider: MockAIProvider):
    """Verify that when revised has no items, all original items are removed."""
    orig = [
        LineItem(name="Old Item 1", total_price=100.0),
        LineItem(name="Old Item 2", total_price=200.0),
    ]
    matches = mock_provider.match_line_items(orig, [])
    assert len(matches) == 2
    for m in matches:
        assert m.original_item is not None
        assert m.revised_item is None
        assert m.confidence_score == 1.0
        assert m.confidence_level == ConfidenceLevel.CONFIRMED
        assert "removed" in (m.rationale or "").lower()


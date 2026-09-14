"""
Domain models and data contracts for commercial offer comparison.
Defines strict Pydantic v2 models for extraction, audit, matching, and diff reports.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ChangeType(str, Enum):
    """Substantive change types detected between offer versions."""
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    RENAMED = "RENAMED"
    QUANTITY_CHANGED = "QUANTITY_CHANGED"
    UNIT_PRICE_CHANGED = "UNIT_PRICE_CHANGED"
    TOTAL_CHANGED = "TOTAL_CHANGED"
    DELIVERY_DATE_CHANGED = "DELIVERY_DATE_CHANGED"


class ConfidenceLevel(str, Enum):
    """Certainty level for semantic matching and change classification."""
    CONFIRMED = "CONFIRMED"
    UNCERTAIN = "UNCERTAIN"


class SourceReference(BaseModel):
    """Traceable citation pointing to the exact PDF page and source text snippet."""
    model_config = ConfigDict(extra="ignore")

    page_number: int = Field(..., ge=1, description="1-indexed page number in the source PDF")
    snippet: str = Field(..., min_length=1, description="Verbatim quote or text excerpt from the document")


class LineItem(BaseModel):
    """An individual product or service line item in a commercial offer."""
    model_config = ConfigDict(extra="ignore")

    item_id: str | None = Field(default=None, description="Optional unique identifier or row key")
    name: str = Field(..., min_length=1, description="Item name or primary title")
    description: str | None = Field(default=None, description="Detailed item specification or notes")
    quantity: float | None = Field(default=None, description="Quantity offered")
    unit: str | None = Field(default=None, description="Unit of measurement (e.g. pcs, hrs, m2)")
    unit_price: float | None = Field(default=None, description="Price per unit")
    total_price: float | None = Field(default=None, description="Total price for this line item")
    source_ref: SourceReference | None = Field(default=None, description="Source citation in the PDF")


class OfferDocument(BaseModel):
    """Structured data extracted from a single commercial offer document."""
    model_config = ConfigDict(extra="ignore")

    vendor_name: str | None = Field(default=None, description="Vendor / supplier company name")
    client_name: str | None = Field(default=None, description="Client / recipient company name")
    offer_id: str | None = Field(default=None, description="Offer, quote, or proposal number")
    offer_date: str | None = Field(default=None, description="Date of issue")
    delivery_date: str | None = Field(default=None, description="Proposed delivery date or lead time")
    currency: str | None = Field(default=None, description="Currency code or symbol (e.g. USD, EUR, UAH)")
    items: list[LineItem] = Field(default_factory=list, description="Extracted line items")
    subtotal: float | None = Field(default=None, description="Subtotal before taxes or discounts")
    tax: float | None = Field(default=None, description="Applicable tax or VAT amount")
    grand_total: float | None = Field(default=None, description="Final payable amount")


class MathDiscrepancy(BaseModel):
    """Detailed record of an arithmetic discrepancy detected in a source document."""
    model_config = ConfigDict(extra="ignore")

    location: str = Field(..., description="Location of error (e.g. 'Line item: Widget A', 'Document Totals')")
    expected_value: float = Field(..., description="Expected value computed deterministically")
    actual_value: float = Field(..., description="Actual value extracted from the source PDF")
    message: str = Field(..., description="Human-readable explanation of the discrepancy")


class AuditReport(BaseModel):
    """Deterministic mathematical verification report for an offer document."""
    model_config = ConfigDict(extra="ignore")

    document_name: str = Field(..., description="Document identifier (e.g. 'Original Offer', 'Revised Offer')")
    is_valid: bool = Field(..., description="True if no arithmetic discrepancies were found")
    discrepancies: list[MathDiscrepancy] = Field(default_factory=list, description="List of math discrepancies")


class DetectedChange(BaseModel):
    """A substantive change detected between the original and revised commercial offers."""
    model_config = ConfigDict(extra="ignore")

    change_type: ChangeType = Field(..., description="Classification of the change")
    item_name_original: str | None = Field(default=None, description="Original item name (if applicable)")
    item_name_revised: str | None = Field(default=None, description="Revised item name (if applicable)")
    original_value: Any = Field(default=None, description="Previous value or details")
    revised_value: Any = Field(default=None, description="New value or details")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.CONFIRMED, description="Confidence level")
    explanation: str = Field(..., min_length=1, description="Human-readable explanation of why this change occurred")
    original_source_ref: SourceReference | None = Field(default=None, description="Source reference in original PDF")
    revised_source_ref: SourceReference | None = Field(default=None, description="Source reference in revised PDF")


class TokenUsage(BaseModel):
    """Token consumption and estimated cost metrics for LLM operations."""
    model_config = ConfigDict(extra="ignore")

    prompt_tokens: int = Field(default=0, ge=0, description="Tokens in prompt / input")
    completion_tokens: int = Field(default=0, ge=0, description="Tokens generated in completion / output")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens consumed")
    estimated_cost_usd: float = Field(default=0.0, ge=0.0, description="Estimated total cost in USD")


class ComparisonSummary(BaseModel):
    """Summary metrics of the comparison between two offers."""
    model_config = ConfigDict(extra="allow")

    total_changes: int = Field(default=0, description="Total count of substantive changes")
    added_items_count: int = Field(default=0, description="Count of added line items")
    removed_items_count: int = Field(default=0, description="Count of removed line items")
    modified_items_count: int = Field(default=0, description="Count of modified line items")
    has_arithmetic_errors: bool = Field(default=False, description="True if either document has math errors")
    price_difference: float | None = Field(default=None, description="revised_grand_total - original_grand_total")
    original_grand_total: float | None = Field(default=None, description="Original grand total")
    revised_grand_total: float | None = Field(default=None, description="Revised grand total")
    currency: str | None = Field(default=None, description="Currency of comparison")
    processing_time_ms: float | None = Field(default=None, description="Total processing time in milliseconds")
    token_usage: TokenUsage | None = Field(default=None, description="Token usage breakdown")
    estimated_cost_usd: float | None = Field(default=None, description="Estimated cost in USD")


class ComparisonReport(BaseModel):
    """Complete end-to-end report comparing original and revised offers."""
    model_config = ConfigDict(extra="ignore")

    original_document: OfferDocument | None = Field(default=None, description="Extracted original offer data")
    revised_document: OfferDocument | None = Field(default=None, description="Extracted revised offer data")
    original_audit: AuditReport = Field(..., description="Arithmetic audit for original offer")
    revised_audit: AuditReport = Field(..., description="Arithmetic audit for revised offer")
    changes: list[DetectedChange] = Field(default_factory=list, description="Substantive changes detected")
    summary: ComparisonSummary | dict[str, Any] = Field(default_factory=ComparisonSummary, description="Summary statistics")
    processing_time_ms: float | None = Field(default=None, description="Total processing time in milliseconds")
    token_usage: TokenUsage | None = Field(default=None, description="Token usage breakdown")
    estimated_cost_usd: float | None = Field(default=None, description="Estimated cost in USD")


class PageContent(BaseModel):
    """Raw text and metadata extracted from a single PDF page."""
    model_config = ConfigDict(extra="ignore")

    page_number: int = Field(..., ge=1, description="1-indexed page number")
    raw_text: str = Field(default="", description="Extracted textual content")
    lines: list[str] = Field(default_factory=list, description="Extracted text lines")


class ItemMatch(BaseModel):
    """Semantic match between an original and a revised line item."""
    model_config = ConfigDict(extra="ignore")

    original_item: LineItem | None = Field(default=None, description="Original item or None if added")
    revised_item: LineItem | None = Field(default=None, description="Revised item or None if removed")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Semantic match confidence (0.0 to 1.0)")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.CONFIRMED, description="Confidence category")
    rationale: str | None = Field(default=None, description="Reasoning behind semantic match")

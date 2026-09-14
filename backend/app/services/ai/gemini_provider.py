"""
Google Gemini Flash AI Provider using the official google-genai SDK.
Provides structured JSON extraction, semantic matching with confidence scoring,
and precise token usage accounting.
"""

from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.schemas import (
    ConfidenceLevel,
    ItemMatch,
    LineItem,
    OfferDocument,
    PageContent,
)
from app.services.ai.base import BaseAIProvider
from app.services.ai.prompts import (
    EXTRACTION_SYSTEM_INSTRUCTION,
    MATCHING_SYSTEM_INSTRUCTION,
    build_extraction_prompt,
    build_matching_prompt,
)
from app.services.pdf_extractor import find_source_snippet

logger = logging.getLogger(__name__)


class RawItemMatch(BaseModel):
    """Internal model for structured LLM line item matching response."""
    original_index: int | None = Field(
        default=None,
        description="0-indexed position in original_items list, or null if item is newly added",
    )
    revised_index: int | None = Field(
        default=None,
        description="0-indexed position in revised_items list, or null if item was removed",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Match confidence score between 0.0 and 1.0",
    )
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.CONFIRMED,
        description="'CONFIRMED' if score >= 0.8, otherwise 'UNCERTAIN'",
    )
    rationale: str = Field(
        ...,
        min_length=1,
        description="Clear explanation of why these items match or why addition/removal occurred",
    )


class RawMatchResponse(BaseModel):
    """Wrapper model for structured matching list."""
    matches: list[RawItemMatch] = Field(default_factory=list)


class GeminiFlashProvider(BaseAIProvider):
    """
    Production AI provider utilizing Google Gemini Flash models (gemini-2.5-flash)
    for zero-shot structured extraction and semantic contract line item matching.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        super().__init__()
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.client: genai.Client | None = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _ensure_client(self) -> genai.Client:
        """Ensure client is configured with an active API key."""
        if self.client is None:
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please provide an API key via environment "
                "variable or initialize GeminiFlashProvider(api_key=...)."
            )
        return self.client

    def extract_offer_data(self, pages: list[PageContent]) -> OfferDocument:
        """
        Extract structured commercial offer data from page contents using Gemini Flash.
        Enforces literal raw values extraction without math recalculation.
        """
        client = self._ensure_client()
        prompt = build_extraction_prompt(pages)

        config = types.GenerateContentConfig(
            system_instruction=EXTRACTION_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=OfferDocument,
            temperature=0.0,
        )

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        # Track token consumption
        prompt_tokens = 0
        completion_tokens = 0
        if response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        self._record_usage(prompt_tokens, completion_tokens)

        # Parse structured output
        raw_text = response.text or "{}"
        offer_doc = OfferDocument.model_validate_json(raw_text)

        # Verify and supplement source references
        for item in offer_doc.items:
            if not item.source_ref or not item.source_ref.snippet:
                item.source_ref = find_source_snippet(pages, item.name)

        return offer_doc

    def match_line_items(
        self,
        original_items: list[LineItem],
        revised_items: list[LineItem],
    ) -> list[ItemMatch]:
        """
        Semantically match line items across original and revised offers using Gemini Flash.
        Handles reordered, renamed, added, and removed items with confidence levels.
        """
        client = self._ensure_client()
        prompt = build_matching_prompt(original_items, revised_items)

        config = types.GenerateContentConfig(
            system_instruction=MATCHING_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=RawMatchResponse,
            temperature=0.0,
        )

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        # Track token consumption
        prompt_tokens = 0
        completion_tokens = 0
        if response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        self._record_usage(prompt_tokens, completion_tokens)

        raw_text = response.text or "{}"
        raw_response = RawMatchResponse.model_validate_json(raw_text)

        matches: list[ItemMatch] = []
        matched_original_indices: set[int] = set()
        matched_revised_indices: set[int] = set()

        for rm in raw_response.matches:
            orig_item = None
            if rm.original_index is not None and 0 <= rm.original_index < len(original_items):
                orig_item = original_items[rm.original_index]
                matched_original_indices.add(rm.original_index)

            rev_item = None
            if rm.revised_index is not None and 0 <= rm.revised_index < len(revised_items):
                rev_item = revised_items[rm.revised_index]
                matched_revised_indices.add(rm.revised_index)

            # Enforce confidence level threshold
            conf_level = (
                ConfidenceLevel.CONFIRMED
                if rm.confidence_score >= 0.8
                else ConfidenceLevel.UNCERTAIN
            )

            matches.append(
                ItemMatch(
                    original_item=orig_item,
                    revised_item=rev_item,
                    confidence_score=rm.confidence_score,
                    confidence_level=conf_level,
                    rationale=rm.rationale,
                )
            )

        # Fallback guard: check if any items were completely omitted by the model
        for r_idx, rev in enumerate(revised_items):
            if r_idx not in matched_revised_indices:
                matches.append(
                    ItemMatch(
                        original_item=None,
                        revised_item=rev,
                        confidence_score=1.0,
                        confidence_level=ConfidenceLevel.CONFIRMED,
                        rationale=f"Added item: '{rev.name}'",
                    )
                )

        for o_idx, orig in enumerate(original_items):
            if o_idx not in matched_original_indices:
                matches.append(
                    ItemMatch(
                        original_item=orig,
                        revised_item=None,
                        confidence_score=1.0,
                        confidence_level=ConfidenceLevel.CONFIRMED,
                        rationale=f"Removed item: '{orig.name}'",
                    )
                )

        return matches

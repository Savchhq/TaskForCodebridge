"""
Abstract base class and contract for AI providers.
Defines structured extraction, semantic line item matching,
and token usage / cost accounting.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.schemas import (
    ConfidenceLevel,
    ItemMatch,
    LineItem,
    OfferDocument,
    PageContent,
    TokenUsage,
)

# Gemini 2.5 Flash pricing assumptions ($ per million tokens)
GEMINI_FLASH_INPUT_RATE_PER_M = 0.075
GEMINI_FLASH_OUTPUT_RATE_PER_M = 0.30


def calculate_gemini_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculate estimated cost in USD based on Gemini Flash pricing rates.

    Input: $0.075 / 1M tokens
    Output: $0.30 / 1M tokens
    """
    cost = (
        (prompt_tokens * GEMINI_FLASH_INPUT_RATE_PER_M / 1_000_000.0)
        + (completion_tokens * GEMINI_FLASH_OUTPUT_RATE_PER_M / 1_000_000.0)
    )
    return round(cost, 6)


class BaseAIProvider(ABC):
    """
    Abstract interface for AI providers powering commercial offer extraction
    and semantic line item matching.
    """

    def __init__(self) -> None:
        self._last_token_usage = TokenUsage()
        self._cumulative_token_usage = TokenUsage()

    @property
    def last_token_usage(self) -> TokenUsage:
        """Token usage from the most recent LLM invocation."""
        return self._last_token_usage

    @property
    def cumulative_token_usage(self) -> TokenUsage:
        """Cumulative token usage across all invocations in this provider session."""
        return self._cumulative_token_usage

    def _record_usage(self, prompt_tokens: int, completion_tokens: int) -> TokenUsage:
        """Record token consumption and compute estimated USD cost."""
        total = prompt_tokens + completion_tokens
        cost = calculate_gemini_cost(prompt_tokens, completion_tokens)
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
        )
        self._last_token_usage = usage

        self._cumulative_token_usage = TokenUsage(
            prompt_tokens=self._cumulative_token_usage.prompt_tokens + prompt_tokens,
            completion_tokens=self._cumulative_token_usage.completion_tokens + completion_tokens,
            total_tokens=self._cumulative_token_usage.total_tokens + total,
            estimated_cost_usd=round(
                self._cumulative_token_usage.estimated_cost_usd + cost, 6
            ),
        )
        return usage

    def reset_token_usage(self) -> None:
        """Reset session token usage counters."""
        self._last_token_usage = TokenUsage()
        self._cumulative_token_usage = TokenUsage()

    @abstractmethod
    def extract_offer_data(self, pages: list[PageContent]) -> OfferDocument:
        """
        Extract structured commercial offer data from page contents.

        Args:
            pages: List of PageContent objects extracted from the PDF.

        Returns:
            OfferDocument containing header fields and extracted line items.
        """
        pass

    @abstractmethod
    def match_line_items(
        self,
        original_items: list[LineItem],
        revised_items: list[LineItem],
    ) -> list[ItemMatch]:
        """
        Semantically match line items across original and revised offers.

        Must identify:
        - Exact and renamed matches (with confidence score & rationale).
        - Added items (original_item=None).
        - Removed items (revised_item=None).
        - Confidence level (CONFIRMED if score >= 0.8, else UNCERTAIN).

        Args:
            original_items: List of line items from original offer.
            revised_items: List of line items from revised offer.

        Returns:
            List of ItemMatch objects.
        """
        pass

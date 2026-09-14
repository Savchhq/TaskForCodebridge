"""
AI Services package providing swappable LLM providers for commercial offer comparison.
"""

from app.core.config import settings
from app.services.ai.base import BaseAIProvider, calculate_gemini_cost
from app.services.ai.gemini_provider import GeminiFlashProvider
from app.services.ai.mock_provider import MockAIProvider


def get_ai_provider(provider_type: str = "auto") -> BaseAIProvider:
    """
    Factory function to obtain an AI provider instance.

    Args:
        provider_type: "mock", "gemini", or "auto".
                       "auto" selects GeminiFlashProvider if GEMINI_API_KEY
                       is configured; otherwise falls back to MockAIProvider.

    Returns:
        BaseAIProvider instance.
    """
    normalized = provider_type.strip().lower()

    if normalized == "mock":
        return MockAIProvider()

    if normalized == "gemini":
        return GeminiFlashProvider()

    if normalized == "auto":
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            return GeminiFlashProvider()
        return MockAIProvider()

    raise ValueError(f"Unknown AI provider type: '{provider_type}'. Valid options: 'auto', 'gemini', 'mock'.")


__all__ = [
    "BaseAIProvider",
    "GeminiFlashProvider",
    "MockAIProvider",
    "calculate_gemini_cost",
    "get_ai_provider",
]

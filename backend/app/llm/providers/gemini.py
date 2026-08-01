"""
backend/app/llm/providers/gemini.py — Gemini LLM Provider Foundation.

Inherits from BaseLLMProvider and raises NotImplementedError for generation/streaming.
"""

from typing import AsyncIterator, Optional

from app.llm.base import BaseLLMProvider
from app.llm.config import LLMConfig
from app.llm.models import LLMRequest, LLMResponse, ProviderType


class GeminiProvider(BaseLLMProvider):
    """
    Gemini LLM Provider implementation stub.
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        super().__init__(config=config, provider_type=ProviderType.GEMINI)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously generate Gemini completion."""
        raise NotImplementedError("Gemini API generate() integration is not yet implemented.")

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Asynchronously stream Gemini completion tokens."""
        raise NotImplementedError("Gemini API stream() integration is not yet implemented.")
        yield ""

    async def health_check(self) -> bool:
        """Check Gemini API endpoint connectivity."""
        raise NotImplementedError("Gemini API health_check() is not yet implemented.")

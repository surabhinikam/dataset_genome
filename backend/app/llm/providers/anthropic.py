"""
backend/app/llm/providers/anthropic.py — Anthropic LLM Provider Foundation.

Inherits from BaseLLMProvider and raises NotImplementedError for generation/streaming.
"""

from typing import AsyncIterator, Optional

from app.llm.base import BaseLLMProvider
from app.llm.config import LLMConfig
from app.llm.models import LLMRequest, LLMResponse, ProviderType


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic LLM Provider implementation stub.
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        super().__init__(config=config, provider_type=ProviderType.ANTHROPIC)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously generate Anthropic completion."""
        raise NotImplementedError("Anthropic API generate() integration is not yet implemented.")

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Asynchronously stream Anthropic completion tokens."""
        raise NotImplementedError("Anthropic API stream() integration is not yet implemented.")
        yield ""

    async def health_check(self) -> bool:
        """Check Anthropic API endpoint connectivity."""
        raise NotImplementedError("Anthropic API health_check() is not yet implemented.")

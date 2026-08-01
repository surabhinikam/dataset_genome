"""
backend/app/llm/providers/ollama.py — Ollama LLM Provider Foundation.

Inherits from BaseLLMProvider and raises NotImplementedError for generation/streaming.
"""

from typing import AsyncIterator, Optional

from app.llm.base import BaseLLMProvider
from app.llm.config import LLMConfig
from app.llm.models import LLMRequest, LLMResponse, ProviderType


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM Provider implementation stub.
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        super().__init__(config=config, provider_type=ProviderType.OLLAMA)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously generate Ollama completion."""
        raise NotImplementedError("Ollama API generate() integration is not yet implemented.")

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Asynchronously stream Ollama completion tokens."""
        raise NotImplementedError("Ollama API stream() integration is not yet implemented.")
        yield ""

    async def health_check(self) -> bool:
        """Check Ollama API endpoint connectivity."""
        raise NotImplementedError("Ollama API health_check() is not yet implemented.")

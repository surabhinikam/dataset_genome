"""
backend/app/llm/base.py — Abstract Base Provider Class for LLM Module.

Defines BaseLLMProvider abstract base class with generate(), stream(), and health_check().
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from app.llm.config import DEFAULT_LLM_CONFIG, LLMConfig
from app.llm.models import LLMRequest, LLMResponse, ProviderType


class BaseLLMProvider(ABC):
    """
    Abstract Base Class for all LLM Provider implementations.
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        provider_type: ProviderType = ProviderType.OPENAI,
    ) -> None:
        self.config = config or DEFAULT_LLM_CONFIG
        self.provider_type = provider_type

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Asynchronously generate text completion for the given LLMRequest.
        """
        pass

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """
        Asynchronously stream text tokens for the given LLMRequest.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Asynchronously check provider API connectivity and health status.
        """
        pass

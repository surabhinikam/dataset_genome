"""
backend/app/llm/factory.py — LLM Factory for Provider Resolution.

Implements LLMFactory to resolve and instantiate LLM provider instances based on ProviderType enum or string.
Raises ProviderNotFoundError for unsupported provider types.
"""

import logging
from typing import Dict, Optional, Type, Union

from app.llm.base import BaseLLMProvider
from app.llm.config import DEFAULT_LLM_CONFIG, LLMConfig
from app.llm.exceptions import ProviderNotFoundError
from app.llm.models import ProviderType
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.gemini import GeminiProvider
from app.llm.providers.ollama import OllamaProvider
from app.llm.providers.openai import OpenAIProvider

logger = logging.getLogger("dataset_genome.llm.factory")


class LLMFactory:
    """
    Factory pattern for creating and resolving LLM provider instances.
    """

    _registry: Dict[ProviderType, Type[BaseLLMProvider]] = {
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.ANTHROPIC: AnthropicProvider,
        ProviderType.GEMINI: GeminiProvider,
        ProviderType.OLLAMA: OllamaProvider,
    }

    @classmethod
    def register_provider(cls, provider_type: ProviderType, provider_cls: Type[BaseLLMProvider]) -> None:
        """Register or override a provider class in the factory registry."""
        cls._registry[provider_type] = provider_cls
        logger.info(f"LLMFactory registered provider '{provider_type.value}' -> {provider_cls.__name__}.")

    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[Union[str, ProviderType]] = None,
        config: Optional[LLMConfig] = None,
    ) -> BaseLLMProvider:
        """
        Instantiate and return a BaseLLMProvider instance for the specified provider_type.
        Defaults to config.default_provider if provider_type is omitted.
        """
        cfg = config or DEFAULT_LLM_CONFIG
        p_type = provider_type or cfg.default_provider

        # Convert string input to ProviderType enum if necessary
        if isinstance(p_type, str):
            try:
                enum_type = ProviderType(p_type.lower())
            except ValueError:
                raise ProviderNotFoundError(
                    f"Unsupported LLM provider type '{p_type}'. Supported providers: {[p.value for p in ProviderType]}",
                    provider=str(p_type),
                )
        else:
            enum_type = p_type

        provider_cls = cls._registry.get(enum_type)
        if not provider_cls:
            raise ProviderNotFoundError(
                f"Provider class for '{enum_type.value}' is not registered in LLMFactory.",
                provider=enum_type.value,
            )

        logger.info(f"LLMFactory created instance of '{provider_cls.__name__}' for provider '{enum_type.value}'.")
        return provider_cls(config=cfg)

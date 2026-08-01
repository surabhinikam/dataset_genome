"""
backend/app/llm — Foundation LLM Module for Dataset Genome.

Provides a unified, strongly-typed abstraction layer for Large Language Model providers
(OpenAI, Anthropic, Gemini, Ollama) using Pydantic v2.
"""

from app.llm.base import BaseLLMProvider
from app.llm.config import DEFAULT_LLM_CONFIG, LLMConfig, get_llm_config
from app.llm.exceptions import (
    APIConnectionError,
    AuthenticationError,
    InvalidRequestError,
    LLMException,
    ProviderNotFoundError,
    ProviderTimeoutError,
    RateLimitError,
)
from app.llm.factory import LLMFactory
from app.llm.models import LLMMessage, LLMRequest, LLMResponse, ProviderType, TokenUsage
from app.llm.providers import AnthropicProvider, GeminiProvider, OllamaProvider, OpenAIProvider
from app.llm.utils import (
    estimate_token_count,
    messages_to_prompt,
    normalize_request,
    prompt_to_messages,
    validate_llm_request,
)

__all__ = [
    "BaseLLMProvider",
    "LLMFactory",
    "LLMConfig",
    "DEFAULT_LLM_CONFIG",
    "get_llm_config",
    "ProviderType",
    "LLMMessage",
    "LLMRequest",
    "LLMResponse",
    "TokenUsage",
    "LLMException",
    "AuthenticationError",
    "RateLimitError",
    "ProviderNotFoundError",
    "InvalidRequestError",
    "APIConnectionError",
    "ProviderTimeoutError",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "OllamaProvider",
    "normalize_request",
    "messages_to_prompt",
    "prompt_to_messages",
    "estimate_token_count",
    "validate_llm_request",
]

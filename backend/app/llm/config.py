"""
backend/app/llm/config.py — Configuration for LLM Module.

Defines LLMConfig Pydantic v2 model reading provider keys and settings from environment variables.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field

from app.llm.models import ProviderType


class LLMConfig(BaseModel):
    """
    Configuration parameters for LLM providers read from environment variables.
    """

    default_provider: ProviderType = Field(
        default=ProviderType.OPENAI,
        description="Default LLM provider type",
    )
    default_model: str = Field(
        default="gpt-4o",
        description="Default model identifier",
    )
    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="OpenAI API key",
    )
    anthropic_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"),
        description="Anthropic API key",
    )
    gemini_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY"),
        description="Gemini API key",
    )
    ollama_base_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        description="Ollama local server base URL",
    )
    request_timeout: float = Field(
        default=60.0,
        ge=1.0,
        description="LLM request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts on transient network errors",
    )


def get_llm_config() -> LLMConfig:
    """Instantiate and return LLMConfig loaded from environment variables."""
    return LLMConfig()


DEFAULT_LLM_CONFIG = get_llm_config()

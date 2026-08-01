"""
backend/app/llm/models.py — Pydantic v2 Models and Enums for LLM Module.

Defines ProviderType enum, LLMMessage, LLMRequest, TokenUsage, and LLMResponse Pydantic v2 models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """Supported LLM provider types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class LLMMessage(BaseModel):
    """Individual message in a conversational LLM request."""

    role: str = Field(..., description="Message sender role e.g. 'system', 'user', 'assistant'")
    content: str = Field(..., description="Message text content")
    name: Optional[str] = Field(None, description="Optional author name identifier")


class LLMRequest(BaseModel):
    """Standardized LLM request model."""

    prompt: Optional[str] = Field(None, description="Single prompt string (alternative to messages)")
    messages: List[LLMMessage] = Field(default_factory=list, description="Structured message list")
    model: str = Field("default", description="Target model identifier e.g. 'gpt-4o', 'claude-3-5-sonnet'")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature [0.0..2.0]")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum completion token count")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling probability")
    stop_sequences: List[str] = Field(default_factory=list, description="Stop sequence triggers")
    stream: bool = Field(False, description="Stream response tokens flag")
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific extra parameters")


class TokenUsage(BaseModel):
    """Token consumption metrics."""

    prompt_tokens: int = Field(0, ge=0, description="Tokens consumed in prompt")
    completion_tokens: int = Field(0, ge=0, description="Tokens generated in completion")
    total_tokens: int = Field(0, ge=0, description="Total tokens consumed")


class LLMResponse(BaseModel):
    """Standardized LLM response model."""

    content: str = Field(..., description="Generated text response content")
    provider: ProviderType = Field(..., description="Provider executing the request")
    model: str = Field(..., description="Model version used for generation")
    usage: TokenUsage = Field(default_factory=TokenUsage, description="Token consumption breakdown")
    finish_reason: Optional[str] = Field(None, description="Completion finish reason e.g. 'stop', 'length'")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw provider response payload")
    latency_seconds: float = Field(0.0, ge=0.0, description="Request execution duration in seconds")
    estimated_cost_usd: Optional[float] = Field(None, ge=0.0, description="Approximate cost in USD based on token usage")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

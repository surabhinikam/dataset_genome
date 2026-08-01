"""
backend/app/llm/providers/openai.py — OpenAI LLM Provider Implementation.

Implements BaseLLMProvider for OpenAI using the official openai SDK (v2).
Features:
  - Async client initialization from LLMConfig.openai_api_key
  - generate()  : Chat Completions with full LLMResponse population
  - stream()    : Streaming token-by-token via AsyncIterator[str]
  - health_check(): Lightweight models.list() probe
  - Tenacity retry policy for transient errors
  - Full SDK → custom exception mapping (no raw SDK exceptions escape)
  - Approximate cost estimation from known per-model pricing tables
"""

from __future__ import annotations

import logging
import time
from typing import AsyncIterator, Dict, List, Optional

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.llm.base import BaseLLMProvider
from app.llm.config import LLMConfig
from app.llm.exceptions import (
    APIConnectionError,
    AuthenticationError,
    InvalidRequestError,
    LLMException,
    ProviderTimeoutError,
    RateLimitError,
)
from app.llm.models import LLMMessage, LLMRequest, LLMResponse, ProviderType, TokenUsage

logger = logging.getLogger("dataset_genome.llm.openai")

# ---------------------------------------------------------------------------
# Per-model approximate pricing (USD per 1 000 000 tokens, as of mid-2025)
# ---------------------------------------------------------------------------
_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o":               {"prompt": 5.00,   "completion": 15.00},
    "gpt-4o-mini":          {"prompt": 0.15,   "completion": 0.60},
    "gpt-4-turbo":          {"prompt": 10.00,  "completion": 30.00},
    "gpt-4":                {"prompt": 30.00,  "completion": 60.00},
    "gpt-3.5-turbo":        {"prompt": 0.50,   "completion": 1.50},
    "o1":                   {"prompt": 15.00,  "completion": 60.00},
    "o1-mini":              {"prompt": 3.00,   "completion": 12.00},
}

_PROVIDER = ProviderType.OPENAI


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> Optional[float]:
    """Return approximate USD cost for a generation or None if model is unknown."""
    # Normalise: strip version suffixes like "-2024-11-20" to find base key
    base = model
    for key in _MODEL_PRICING:
        if model.startswith(key):
            base = key
            break

    pricing = _MODEL_PRICING.get(base)
    if pricing is None:
        return None

    cost = (prompt_tokens * pricing["prompt"] + completion_tokens * pricing["completion"]) / 1_000_000
    return round(cost, 8)


def _messages_for_openai(request: LLMRequest) -> List[Dict[str, str]]:
    """
    Convert LLMRequest into the list-of-dicts format expected by the OpenAI API.
    If request.messages is populated it takes priority; otherwise request.prompt
    is wrapped as a single user message.
    """
    if request.messages:
        return [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]
    if request.prompt:
        return [{"role": "user", "content": request.prompt}]
    return []


def _map_openai_error(exc: Exception, model: str) -> LLMException:
    """Translate an openai SDK exception to the appropriate custom exception."""
    provider = _PROVIDER.value

    if isinstance(exc, openai.AuthenticationError):
        return AuthenticationError(
            f"Invalid or missing OpenAI API key: {exc.message}", provider=provider
        )
    if isinstance(exc, openai.RateLimitError):
        return RateLimitError(
            f"OpenAI rate limit exceeded: {exc.message}", provider=provider
        )
    if isinstance(exc, openai.APITimeoutError):
        return ProviderTimeoutError(
            f"OpenAI request timed out for model '{model}'.", provider=provider
        )
    if isinstance(exc, openai.APIConnectionError):
        return APIConnectionError(
            f"Unable to connect to OpenAI API: {exc}", provider=provider
        )
    if isinstance(exc, openai.BadRequestError):
        return InvalidRequestError(
            f"Bad request to OpenAI API: {exc.message}", provider=provider
        )
    # Catch-all for any remaining openai.OpenAIError or other SDK errors
    return LLMException(
        f"OpenAI API error: {exc}", provider=provider
    )


class OpenAIProvider(BaseLLMProvider):
    """
    Full OpenAI LLM Provider implementation backed by the official openai Python SDK (v2).
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        super().__init__(config=config, provider_type=_PROVIDER)
        self._client: Optional[AsyncOpenAI] = None

    # ------------------------------------------------------------------
    # Internal: lazy client construction
    # ------------------------------------------------------------------

    def _get_client(self) -> AsyncOpenAI:
        """Return (lazily constructed) AsyncOpenAI client."""
        if self._client is None:
            api_key = self.config.openai_api_key
            if not api_key:
                raise AuthenticationError(
                    "OPENAI_API_KEY is not set. Please export OPENAI_API_KEY in your environment.",
                    provider=_PROVIDER.value,
                )
            self._client = AsyncOpenAI(
                api_key=api_key,
                timeout=self.config.request_timeout,
                max_retries=0,  # We manage retries via Tenacity ourselves
            )
        return self._client

    # ------------------------------------------------------------------
    # Retry decorator factory — built from config at call time
    # ------------------------------------------------------------------

    def _make_retry(self):
        """Return a Tenacity retry decorator configured from self.config."""
        return retry(
            reraise=True,
            retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            stop=stop_after_attempt(max(1, self.config.max_retries)),
        )

    # ------------------------------------------------------------------
    # health_check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify API key exists and that the OpenAI API is reachable via a
        lightweight models.list() probe.
        Returns True on success, False on any failure.
        """
        try:
            client = self._get_client()
            await client.models.list()
            logger.debug("OpenAI health_check passed.")
            return True
        except (AuthenticationError, LLMException):
            logger.warning("OpenAI health_check failed: authentication or config error.")
            return False
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI health_check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a text completion via the OpenAI Chat Completions API.

        Workflow:
            LLMRequest  →  OpenAI messages  →  API call  →  extract text
            →  extract token usage  →  measure latency  →  estimate cost
            →  return LLMResponse
        """
        client = self._get_client()
        messages = _messages_for_openai(request)
        if not messages:
            raise InvalidRequestError(
                "LLMRequest must provide either 'prompt' or 'messages'.",
                provider=_PROVIDER.value,
            )

        model = request.model if request.model != "default" else self.config.default_model

        # Build kwargs — only include optional params when the caller set them
        kwargs: Dict = dict(
            model=model,
            messages=messages,
            temperature=request.temperature,
            stream=False,
            **request.extra_params,
        )
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.stop_sequences:
            kwargs["stop"] = request.stop_sequences

        # Wrap the actual API call with Tenacity retries
        @self._make_retry()
        async def _call() -> LLMResponse:
            t_start = time.monotonic()
            try:
                response = await client.chat.completions.create(**kwargs)
            except Exception as exc:
                raise _map_openai_error(exc, model) from exc

            latency = time.monotonic() - t_start

            choice = response.choices[0]
            content = choice.message.content or ""
            finish_reason = choice.finish_reason

            usage_data = response.usage
            usage = TokenUsage(
                prompt_tokens=usage_data.prompt_tokens if usage_data else 0,
                completion_tokens=usage_data.completion_tokens if usage_data else 0,
                total_tokens=usage_data.total_tokens if usage_data else 0,
            )

            estimated_cost = _estimate_cost(
                model, usage.prompt_tokens, usage.completion_tokens
            )

            logger.info(
                "OpenAI generate() completed: model=%s, tokens=%d, latency=%.2fs, cost=$%.6f",
                model,
                usage.total_tokens,
                latency,
                estimated_cost or 0.0,
            )

            return LLMResponse(
                content=content,
                provider=_PROVIDER,
                model=model,
                usage=usage,
                finish_reason=finish_reason,
                raw_response=response.model_dump(),
                latency_seconds=round(latency, 4),
                estimated_cost_usd=estimated_cost,
            )

        return await _call()

    # ------------------------------------------------------------------
    # stream
    # ------------------------------------------------------------------

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """
        Stream text tokens from the OpenAI Chat Completions API.
        Yields each text delta as it arrives.
        """
        client = self._get_client()
        messages = _messages_for_openai(request)
        if not messages:
            raise InvalidRequestError(
                "LLMRequest must provide either 'prompt' or 'messages'.",
                provider=_PROVIDER.value,
            )

        model = request.model if request.model != "default" else self.config.default_model

        kwargs: Dict = dict(
            model=model,
            messages=messages,
            temperature=request.temperature,
            stream=True,
            **request.extra_params,
        )
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            kwargs["top_p"] = request.top_p
        if request.stop_sequences:
            kwargs["stop"] = request.stop_sequences

        try:
            async with await client.chat.completions.create(**kwargs) as stream:
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else None
                    if delta:
                        yield delta
        except Exception as exc:
            raise _map_openai_error(exc, model) from exc

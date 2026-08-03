"""
backend/app/llm/providers/gemini.py — Full Gemini LLM Provider Implementation.

Uses the official google-genai SDK (google.genai), the modern replacement for
the deprecated google.generativeai package.

Features:
  - generate()    : Content generation with full LLMResponse population
  - stream()      : Streaming token-by-token via AsyncIterator[str]
  - health_check(): Lightweight model list probe
  - Full SDK → custom exception mapping (no raw SDK exceptions escape)
  - Approximate token usage from response.usage_metadata
  - Approximate cost estimation (Gemini 2.0 Flash free tier / pay-as-you-go)
"""

from __future__ import annotations

import logging
import time
from typing import AsyncIterator, Dict, List, Optional

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
from app.llm.models import LLMRequest, LLMResponse, ProviderType, TokenUsage

logger = logging.getLogger("dataset_genome.llm.gemini")

_PROVIDER = ProviderType.GEMINI

# ---------------------------------------------------------------------------
# Per-model approximate pricing (USD per 1 000 000 tokens, as of mid-2025)
# Gemini 2.0 Flash is free up to generous quota; pay-as-you-go rates shown.
# ---------------------------------------------------------------------------
_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-2.0-flash":         {"prompt": 0.075,  "completion": 0.30},
    "gemini-2.0-flash-lite":    {"prompt": 0.0375, "completion": 0.15},
    "gemini-1.5-flash":         {"prompt": 0.075,  "completion": 0.30},
    "gemini-1.5-flash-8b":      {"prompt": 0.0375, "completion": 0.15},
    "gemini-1.5-pro":           {"prompt": 1.25,   "completion": 5.00},
    "gemini-2.5-flash":         {"prompt": 0.15,   "completion": 0.60},
    "gemini-2.5-pro":           {"prompt": 1.25,   "completion": 10.00},
}

_DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> Optional[float]:
    """Return approximate USD cost or None if model is unknown."""
    # Match by prefix to handle versioned names like "gemini-2.0-flash-001"
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


def _map_gemini_error(exc: Exception) -> LLMException:
    """Translate a google.genai exception to the appropriate custom exception."""
    provider = _PROVIDER.value
    msg = str(exc)

    # google.genai uses google.api_core.exceptions under the hood
    try:
        from google.api_core import exceptions as api_exc
        if isinstance(exc, api_exc.Unauthenticated):
            return AuthenticationError(f"Invalid or missing Gemini API key: {msg}", provider=provider)
        if isinstance(exc, api_exc.ResourceExhausted):
            return RateLimitError(f"Gemini rate limit exceeded: {msg}", provider=provider)
        if isinstance(exc, api_exc.DeadlineExceeded):
            return ProviderTimeoutError(f"Gemini request timed out: {msg}", provider=provider)
        if isinstance(exc, api_exc.ServiceUnavailable):
            return APIConnectionError(f"Gemini service unavailable: {msg}", provider=provider)
        if isinstance(exc, (api_exc.InvalidArgument, api_exc.BadRequest)):
            return InvalidRequestError(f"Bad request to Gemini API: {msg}", provider=provider)
    except ImportError:
        pass

    # Heuristic string matching as fallback
    low = msg.lower()
    if "api key" in low or "unauthenticated" in low or "invalid argument" in low and "key" in low:
        return AuthenticationError(f"Gemini authentication error: {msg}", provider=provider)
    if "quota" in low or "rate limit" in low or "resource exhausted" in low:
        return RateLimitError(f"Gemini quota exceeded: {msg}", provider=provider)
    if "timeout" in low or "deadline" in low:
        return ProviderTimeoutError(f"Gemini timeout: {msg}", provider=provider)

    return LLMException(f"Gemini API error: {msg}", provider=provider)


def _build_contents(request: LLMRequest) -> List[Dict]:
    """
    Convert LLMRequest to the google.genai contents format.

    google.genai uses: [{"role": "user"|"model", "parts": [{"text": "..."}]}]
    Note: "assistant" role maps to "model" in Gemini's API.
    The system instruction is handled separately via system_instruction param.
    """
    if request.messages:
        contents = []
        for m in request.messages:
            if m.role == "system":
                continue  # system handled separately
            role = "model" if m.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m.content}]})
        return contents

    if request.prompt:
        return [{"role": "user", "parts": [{"text": request.prompt}]}]

    return []


def _extract_system_instruction(request: LLMRequest) -> Optional[str]:
    """Extract the system message content if present in the message list."""
    for m in request.messages:
        if m.role == "system":
            return m.content
    return None


class GeminiProvider(BaseLLMProvider):
    """
    Full Gemini LLM Provider implementation using the official google-genai SDK.
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        super().__init__(config=config, provider_type=_PROVIDER)
        self._client = None

    # ------------------------------------------------------------------
    # Internal: lazy client construction
    # ------------------------------------------------------------------

    def _get_client(self):
        """Return (lazily constructed) google.genai.Client instance."""
        if self._client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise LLMException(
                    "google-genai package is not installed. Run: py -m pip install google-genai",
                    provider=_PROVIDER.value,
                ) from exc

            api_key = self.config.gemini_api_key
            if not api_key:
                raise AuthenticationError(
                    "GEMINI_API_KEY is not set. Please export GEMINI_API_KEY in your environment.",
                    provider=_PROVIDER.value,
                )
            # Explicitly initialize google-genai Client for Google AI Studio (Gemini Developer API)
            self._client = genai.Client(api_key=api_key, vertexai=False)
        return self._client

    def _resolve_model(self, request: LLMRequest) -> str:
        """Resolve the model name, falling back to default."""
        if request.model and request.model != "default":
            return request.model
        # Check if LLMConfig has a Gemini-specific default set; otherwise use ours
        cfg_model = getattr(self.config, "default_model", None)
        if cfg_model and cfg_model != "default" and "gpt" not in cfg_model.lower():
            return cfg_model
        return _DEFAULT_GEMINI_MODEL

    # ------------------------------------------------------------------
    # health_check
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Verify API key exists and Gemini is reachable via a lightweight models list.
        Returns True on success, False on any failure.
        """
        try:
            from google import genai
            client = self._get_client()
            # Lightweight: list first page of models
            client.models.list()
            logger.debug("GeminiProvider health_check passed.")
            return True
        except (AuthenticationError, LLMException):
            logger.warning("GeminiProvider health_check failed: auth/config error.")
            return False
        except Exception as exc:  # noqa: BLE001
            logger.warning("GeminiProvider health_check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a text completion via the Gemini API.

        Workflow:
            LLMRequest → contents + system_instruction → API call
            → extract text → token usage → latency → cost → LLMResponse
        """
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError as exc:
            raise LLMException(
                "google-genai package is not installed. Run: py -m pip install google-genai",
                provider=_PROVIDER.value,
            ) from exc

        client = self._get_client()
        model = self._resolve_model(request)

        contents = _build_contents(request)
        if not contents:
            raise InvalidRequestError(
                "LLMRequest must provide either 'prompt' or 'messages'.",
                provider=_PROVIDER.value,
            )

        system_instruction = _extract_system_instruction(request)

        # Build generation config
        gen_config_kwargs = {
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            gen_config_kwargs["max_output_tokens"] = request.max_tokens
        if request.top_p is not None:
            gen_config_kwargs["top_p"] = request.top_p
        if request.stop_sequences:
            gen_config_kwargs["stop_sequences"] = request.stop_sequences

        gen_config = genai_types.GenerateContentConfig(
            **gen_config_kwargs,
            **({"system_instruction": system_instruction} if system_instruction else {}),
        )

        logger.debug("GeminiProvider.generate(): model=%s, temperature=%.2f", model, request.temperature)

        t_start = time.monotonic()
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=gen_config,
            )
        except Exception as exc:
            raise _map_gemini_error(exc) from exc

        latency = time.monotonic() - t_start

        # Extract text
        content_text = ""
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                content_text = "".join(
                    part.text for part in candidate.content.parts if hasattr(part, "text")
                )

        finish_reason = None
        if response.candidates:
            fr = response.candidates[0].finish_reason
            finish_reason = fr.name if fr else None

        # Token usage from usage_metadata
        usage = TokenUsage()
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            usage = TokenUsage(
                prompt_tokens=getattr(um, "prompt_token_count", 0) or 0,
                completion_tokens=getattr(um, "candidates_token_count", 0) or 0,
                total_tokens=getattr(um, "total_token_count", 0) or 0,
            )

        estimated_cost = _estimate_cost(model, usage.prompt_tokens, usage.completion_tokens)

        logger.info(
            "GeminiProvider.generate() completed: model=%s, tokens=%d, latency=%.2fs, cost=$%.6f",
            model,
            usage.total_tokens,
            latency,
            estimated_cost or 0.0,
        )

        return LLMResponse(
            content=content_text,
            provider=_PROVIDER,
            model=model,
            usage=usage,
            finish_reason=finish_reason,
            raw_response=None,  # google.genai response objects are not JSON-serialisable
            latency_seconds=round(latency, 4),
            estimated_cost_usd=estimated_cost,
        )

    # ------------------------------------------------------------------
    # stream
    # ------------------------------------------------------------------

    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """
        Stream text tokens from the Gemini API.
        Yields each text chunk as it arrives.
        """
        try:
            from google import genai
            from google.genai import types as genai_types
        except ImportError as exc:
            raise LLMException(
                "google-genai package is not installed. Run: py -m pip install google-genai",
                provider=_PROVIDER.value,
            ) from exc

        client = self._get_client()
        model = self._resolve_model(request)

        contents = _build_contents(request)
        if not contents:
            raise InvalidRequestError(
                "LLMRequest must provide either 'prompt' or 'messages'.",
                provider=_PROVIDER.value,
            )

        system_instruction = _extract_system_instruction(request)
        gen_config_kwargs = {"temperature": request.temperature}
        if request.max_tokens is not None:
            gen_config_kwargs["max_output_tokens"] = request.max_tokens
        if request.stop_sequences:
            gen_config_kwargs["stop_sequences"] = request.stop_sequences

        gen_config = genai_types.GenerateContentConfig(
            **gen_config_kwargs,
            **({"system_instruction": system_instruction} if system_instruction else {}),
        )

        try:
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=gen_config,
            ):
                if chunk.candidates:
                    parts = chunk.candidates[0].content.parts if chunk.candidates[0].content else []
                    for part in parts:
                        if hasattr(part, "text") and part.text:
                            yield part.text
        except Exception as exc:
            raise _map_gemini_error(exc) from exc

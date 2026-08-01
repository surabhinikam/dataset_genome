"""
tests/test_openai_provider.py — Unit tests for OpenAIProvider.

All tests mock the OpenAI SDK; no real API calls are made.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import openai

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
from app.llm.providers.openai import OpenAIProvider, _estimate_cost, _messages_for_openai


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(api_key: str = "sk-test-key") -> LLMConfig:
    return LLMConfig(
        openai_api_key=api_key,
        default_model="gpt-4o-mini",
        max_retries=1,
        request_timeout=10.0,
    )


def _fake_usage(prompt: int = 10, completion: int = 20) -> MagicMock:
    u = MagicMock()
    u.prompt_tokens = prompt
    u.completion_tokens = completion
    u.total_tokens = prompt + completion
    return u


def _fake_completion(content: str = "Hello!", finish_reason: str = "stop") -> MagicMock:
    """Build a mock openai.ChatCompletion-style response object."""
    choice = MagicMock()
    choice.message.content = content
    choice.finish_reason = finish_reason

    resp = MagicMock()
    resp.choices = [choice]
    resp.usage = _fake_usage()
    resp.model_dump.return_value = {"id": "chatcmpl-test", "object": "chat.completion"}
    return resp


# ---------------------------------------------------------------------------
# Unit: helpers
# ---------------------------------------------------------------------------

def test_estimate_cost_known_model():
    cost = _estimate_cost("gpt-4o-mini", 1000, 500)
    assert cost is not None
    assert cost > 0


def test_estimate_cost_unknown_model():
    cost = _estimate_cost("some-future-model-xyz", 1000, 500)
    assert cost is None


def test_estimate_cost_versioned_model():
    # e.g. "gpt-4o-2024-11-20" should match "gpt-4o" pricing
    cost = _estimate_cost("gpt-4o-2024-11-20", 1000, 500)
    assert cost is not None
    assert cost > 0


def test_messages_for_openai_from_prompt():
    req = LLMRequest(prompt="Say hello")
    msgs = _messages_for_openai(req)
    assert msgs == [{"role": "user", "content": "Say hello"}]


def test_messages_for_openai_from_messages():
    req = LLMRequest(messages=[
        LLMMessage(role="system", content="You are a scientist."),
        LLMMessage(role="user", content="Explain gravity."),
    ])
    msgs = _messages_for_openai(req)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"


def test_messages_for_openai_empty():
    req = LLMRequest()
    assert _messages_for_openai(req) == []


# ---------------------------------------------------------------------------
# Unit: provider instantiation
# ---------------------------------------------------------------------------

def test_provider_type():
    p = OpenAIProvider(_make_config())
    assert p.provider_type == ProviderType.OPENAI


def test_missing_api_key_raises_on_client_creation():
    p = OpenAIProvider(_make_config(api_key=""))
    p.config.openai_api_key = None
    with pytest.raises(AuthenticationError):
        p._get_client()


# ---------------------------------------------------------------------------
# Unit: generate() — happy path
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_success():
    """generate() returns a populated LLMResponse on successful API call."""
    provider = OpenAIProvider(_make_config())
    fake_resp = _fake_completion(content="Science is wonderful.", finish_reason="stop")

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(return_value=fake_resp)

        # Force the provider to use the patched client
        provider._client = instance

        request = LLMRequest(prompt="What is science?", model="gpt-4o-mini")
        response = await provider.generate(request)

    assert isinstance(response, LLMResponse)
    assert response.content == "Science is wonderful."
    assert response.provider == ProviderType.OPENAI
    assert response.model == "gpt-4o-mini"
    assert response.usage.prompt_tokens == 10
    assert response.usage.completion_tokens == 20
    assert response.usage.total_tokens == 30
    assert response.finish_reason == "stop"
    assert response.latency_seconds >= 0.0
    assert response.estimated_cost_usd is not None
    assert response.raw_response is not None


@pytest.mark.anyio
async def test_generate_uses_default_model_when_not_specified():
    """generate() falls back to config.default_model when model='default'."""
    provider = OpenAIProvider(_make_config())
    fake_resp = _fake_completion()

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.chat.completions.create = AsyncMock(return_value=fake_resp)
        provider._client = instance

        request = LLMRequest(prompt="Hello")
        response = await provider.generate(request)

    assert response.model == "gpt-4o-mini"  # from _make_config()


@pytest.mark.anyio
async def test_generate_passes_temperature_max_tokens():
    """generate() passes temperature and max_tokens correctly to the SDK."""
    provider = OpenAIProvider(_make_config())
    fake_resp = _fake_completion()

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        create_mock = AsyncMock(return_value=fake_resp)
        instance.chat.completions.create = create_mock
        provider._client = instance

        request = LLMRequest(
            prompt="Test prompt",
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=256,
        )
        await provider.generate(request)

    call_kwargs = create_mock.call_args.kwargs
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["max_tokens"] == 256


@pytest.mark.anyio
async def test_generate_empty_request_raises():
    """generate() raises InvalidRequestError when no prompt or messages given."""
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        provider._client = MockClient.return_value

        with pytest.raises(InvalidRequestError):
            await provider.generate(LLMRequest())


# ---------------------------------------------------------------------------
# Unit: generate() — exception mapping
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_maps_authentication_error():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        sdk_exc = openai.AuthenticationError(
            "Invalid API key",
            response=MagicMock(status_code=401),
            body={"error": {"message": "Invalid API key"}},
        )
        instance.chat.completions.create = AsyncMock(side_effect=sdk_exc)
        provider._client = instance

        with pytest.raises(AuthenticationError):
            await provider.generate(LLMRequest(prompt="Hello"))


@pytest.mark.anyio
async def test_generate_maps_rate_limit_error():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        sdk_exc = openai.RateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}},
        )
        instance.chat.completions.create = AsyncMock(side_effect=sdk_exc)
        provider._client = instance

        with pytest.raises(RateLimitError):
            await provider.generate(LLMRequest(prompt="Hello"))


@pytest.mark.anyio
async def test_generate_maps_timeout_error():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        sdk_exc = openai.APITimeoutError(request=MagicMock())
        instance.chat.completions.create = AsyncMock(side_effect=sdk_exc)
        provider._client = instance

        with pytest.raises(ProviderTimeoutError):
            await provider.generate(LLMRequest(prompt="Hello"))


@pytest.mark.anyio
async def test_generate_maps_connection_error():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        sdk_exc = openai.APIConnectionError(request=MagicMock())
        instance.chat.completions.create = AsyncMock(side_effect=sdk_exc)
        provider._client = instance

        with pytest.raises(APIConnectionError):
            await provider.generate(LLMRequest(prompt="Hello"))


@pytest.mark.anyio
async def test_generate_maps_generic_openai_error():
    """Any other OpenAI SDK error maps to base LLMException."""
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        sdk_exc = openai.InternalServerError(
            "Server error",
            response=MagicMock(status_code=500),
            body={"error": {"message": "Server error"}},
        )
        instance.chat.completions.create = AsyncMock(side_effect=sdk_exc)
        provider._client = instance

        with pytest.raises(LLMException):
            await provider.generate(LLMRequest(prompt="Hello"))


# ---------------------------------------------------------------------------
# Unit: health_check()
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_health_check_success():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.models.list = AsyncMock(return_value=[])
        provider._client = instance

        result = await provider.health_check()

    assert result is True


@pytest.mark.anyio
async def test_health_check_returns_false_on_auth_error():
    provider = OpenAIProvider(_make_config())
    provider.config.openai_api_key = None  # Missing key

    result = await provider.health_check()
    assert result is False


@pytest.mark.anyio
async def test_health_check_returns_false_on_connection_error():
    provider = OpenAIProvider(_make_config())

    with patch("app.llm.providers.openai.AsyncOpenAI") as MockClient:
        instance = MockClient.return_value
        instance.models.list = AsyncMock(side_effect=Exception("Connection refused"))
        provider._client = instance

        result = await provider.health_check()

    assert result is False

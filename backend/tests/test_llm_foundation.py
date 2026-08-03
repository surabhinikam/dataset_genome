"""
tests/test_llm_foundation.py — Unit tests for LLM Foundation Module.

Tests models, ProviderType enum, config environment loading, custom exceptions,
LLMFactory provider resolution, BaseLLMProvider inheritance, and utils.
"""

import pytest
from app.llm import (
    APIConnectionError,
    AnthropicProvider,
    AuthenticationError,
    BaseLLMProvider,
    GeminiProvider,
    InvalidRequestError,
    LLMConfig,
    LLMException,
    LLMFactory,
    LLMMessage,
    LLMRequest,
    LLMResponse,
    OllamaProvider,
    OpenAIProvider,
    ProviderNotFoundError,
    ProviderTimeoutError,
    ProviderType,
    RateLimitError,
    TokenUsage,
    estimate_token_count,
    messages_to_prompt,
    normalize_request,
    prompt_to_messages,
    validate_llm_request,
)


def test_provider_type_enum():
    """Test ProviderType enum values."""
    assert ProviderType.OPENAI.value == "openai"
    assert ProviderType.ANTHROPIC.value == "anthropic"
    assert ProviderType.GEMINI.value == "gemini"
    assert ProviderType.OLLAMA.value == "ollama"


def test_pydantic_models():
    """Test LLMMessage, LLMRequest, TokenUsage, and LLMResponse Pydantic v2 models."""
    msg = LLMMessage(role="user", content="Hello world")
    assert msg.role == "user"
    assert msg.content == "Hello world"

    req = LLMRequest(
        prompt="Generate hypothesis",
        model="gpt-4o",
        temperature=0.8,
        messages=[msg],
    )
    assert req.prompt == "Generate hypothesis"
    assert req.model == "gpt-4o"
    assert req.temperature == 0.8
    assert len(req.messages) == 1

    usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    assert usage.total_tokens == 30

    resp = LLMResponse(
        content="Generated text",
        provider=ProviderType.OPENAI,
        model="gpt-4o",
        usage=usage,
        latency_seconds=0.45,
    )
    assert resp.content == "Generated text"
    assert resp.provider == ProviderType.OPENAI
    assert resp.usage.total_tokens == 30


def test_llm_config_env_vars(monkeypatch):
    """Test LLMConfig reading from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-12345")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-abcde")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11435")

    config = LLMConfig()
    assert config.openai_api_key == "sk-test-12345"
    assert config.anthropic_api_key == "sk-ant-abcde"
    assert config.ollama_base_url == "http://localhost:11435"


def test_custom_exceptions():
    """Test custom LLM exception hierarchy."""
    base_exc = LLMException("General error", provider="openai")
    assert str(base_exc) == "[OPENAI] General error"
    assert issubclass(AuthenticationError, LLMException)
    assert issubclass(RateLimitError, LLMException)
    assert issubclass(ProviderNotFoundError, LLMException)
    assert issubclass(InvalidRequestError, LLMException)
    assert issubclass(APIConnectionError, LLMException)
    assert issubclass(ProviderTimeoutError, LLMException)

    auth_err = AuthenticationError("Invalid API key", provider="anthropic")
    assert isinstance(auth_err, LLMException)
    assert str(auth_err) == "[ANTHROPIC] Invalid API key"


def test_llm_factory_provider_resolution():
    """Test LLMFactory resolves provider instances correctly by enum and string."""
    openai_p = LLMFactory.get_provider(ProviderType.OPENAI)
    assert isinstance(openai_p, OpenAIProvider)
    assert isinstance(openai_p, BaseLLMProvider)

    anthropic_p = LLMFactory.get_provider("anthropic")
    assert isinstance(anthropic_p, AnthropicProvider)

    gemini_p = LLMFactory.get_provider("gemini")
    assert isinstance(gemini_p, GeminiProvider)

    ollama_p = LLMFactory.get_provider("ollama")
    assert isinstance(ollama_p, OllamaProvider)


def test_llm_factory_unsupported_provider():
    """Test LLMFactory raises ProviderNotFoundError for invalid provider names."""
    with pytest.raises(ProviderNotFoundError) as exc_info:
        LLMFactory.get_provider("unsupported_llm_provider")
    assert "Unsupported LLM provider type" in str(exc_info.value)


@pytest.mark.anyio
async def test_stub_providers_raise_not_implemented():
    """Anthropic and Ollama are still stubs — they must raise NotImplementedError."""
    stub_providers = [
        AnthropicProvider(),
        OllamaProvider(),
    ]

    request = LLMRequest(prompt="Test prompt", model="test-model")

    for p in stub_providers:
        assert isinstance(p, BaseLLMProvider)

        with pytest.raises(NotImplementedError):
            await p.generate(request)

        with pytest.raises(NotImplementedError):
            await p.health_check()

        with pytest.raises(NotImplementedError):
            stream_gen = p.stream(request)
            await stream_gen.__anext__()


@pytest.mark.anyio
async def test_gemini_provider_inheritance_and_requires_key():
    """
    GeminiProvider is now a real implementation:
    - It must inherit from BaseLLMProvider.
    - Without an API key it raises AuthenticationError (not NotImplementedError).
    - health_check() returns False gracefully instead of raising.
    """
    from app.llm.exceptions import AuthenticationError

    provider = GeminiProvider()
    provider.config.gemini_api_key = None  # Ensure no key is set

    assert isinstance(provider, BaseLLMProvider)

    request = LLMRequest(prompt="Test prompt", model="test-model")

    with pytest.raises(AuthenticationError):
        await provider.generate(request)

    result = await provider.health_check()
    assert result is False


@pytest.mark.anyio
async def test_openai_provider_inheritance_and_requires_key():
    """
    OpenAIProvider is now a real implementation:
    - It must inherit from BaseLLMProvider.
    - Without an API key it raises AuthenticationError (not NotImplementedError).
    - health_check() returns False gracefully instead of raising.
    """
    from app.llm.exceptions import AuthenticationError

    provider = OpenAIProvider()
    provider.config.openai_api_key = None  # Ensure no key is set

    assert isinstance(provider, BaseLLMProvider)

    request = LLMRequest(prompt="Test prompt", model="test-model")

    with pytest.raises(AuthenticationError):
        await provider.generate(request)

    # health_check must not leak exceptions — returns False when key is missing
    result = await provider.health_check()
    assert result is False


def test_utils_functions():
    """Test LLM utility functions."""
    prompt = "What is gravity?"
    msgs = prompt_to_messages(prompt, system_prompt="You are a physics expert.")
    assert len(msgs) == 2
    assert msgs[0].role == "system"
    assert msgs[1].role == "user"

    formatted = messages_to_prompt(msgs)
    assert "[SYSTEM]" in formatted
    assert "[USER]" in formatted

    req = LLMRequest(prompt="Explain quantum physics")
    norm_req = normalize_request(req)
    assert len(norm_req.messages) == 1
    assert norm_req.messages[0].content == "Explain quantum physics"

    est_tokens = estimate_token_count("Hello world test")
    assert est_tokens > 0

    with pytest.raises(InvalidRequestError):
        validate_llm_request(LLMRequest())

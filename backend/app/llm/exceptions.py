"""
backend/app/llm/exceptions.py — Custom Exception Hierarchy for LLM Module.

Defines base exception class LLMException and specific exception subclasses:
- AuthenticationError
- RateLimitError
- ProviderNotFoundError
- InvalidRequestError
- APIConnectionError
- ProviderTimeoutError
"""


class LLMException(Exception):
    """Base exception class for all LLM module errors."""

    def __init__(self, message: str, provider: str = "unknown") -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider

    def __str__(self) -> str:
        return f"[{self.provider.upper()}] {self.message}"


class AuthenticationError(LLMException):
    """Raised when API key or authentication credentials fail."""

    pass


class RateLimitError(LLMException):
    """Raised when provider rate limit or quota is exceeded."""

    pass


class ProviderNotFoundError(LLMException):
    """Raised when a requested LLM provider type is unsupported or unregistered."""

    pass


class InvalidRequestError(LLMException):
    """Raised when request parameters are malformed or invalid."""

    pass


class APIConnectionError(LLMException):
    """Raised when the LLM provider endpoint is unreachable."""

    pass


class ProviderTimeoutError(LLMException):
    """Raised when an LLM provider request times out."""

    pass

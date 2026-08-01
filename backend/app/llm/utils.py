"""
backend/app/llm/utils.py — Helper Utilities for LLM Module.

Provides message normalization, token estimation, and request validation helper functions.
"""

from typing import List

from app.llm.exceptions import InvalidRequestError
from app.llm.models import LLMMessage, LLMRequest


def normalize_request(request: LLMRequest) -> LLMRequest:
    """
    Ensure request has both prompt and messages populated consistently.
    """
    req_dict = request.model_dump()

    if not request.messages and request.prompt:
        req_dict["messages"] = [LLMMessage(role="user", content=request.prompt).model_dump()]
    elif request.messages and not request.prompt:
        req_dict["prompt"] = messages_to_prompt(request.messages)

    return LLMRequest.model_validate(req_dict)


def messages_to_prompt(messages: List[LLMMessage]) -> str:
    """
    Convert a list of LLMMessage objects into a single formatted prompt string.
    """
    parts = []
    for msg in messages:
        role_prefix = f"[{msg.role.upper()}]"
        if msg.name:
            role_prefix += f" ({msg.name})"
        parts.append(f"{role_prefix}\n{msg.content}")
    return "\n\n".join(parts)


def prompt_to_messages(prompt: str, system_prompt: str = "") -> List[LLMMessage]:
    """
    Convert a prompt string and optional system prompt into a structured LLMMessage list.
    """
    messages = []
    if system_prompt:
        messages.append(LLMMessage(role="system", content=system_prompt))
    messages.append(LLMMessage(role="user", content=prompt))
    return messages


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for a text string using standard word/character heuristics (approx 4 chars per token).
    """
    if not text:
        return 0
    return max(1, int(round(len(text) / 4.0)))


def validate_llm_request(request: LLMRequest) -> None:
    """
    Validate that LLMRequest has either prompt or messages provided.
    Raises InvalidRequestError if request is invalid.
    """
    if not request.prompt and not request.messages:
        raise InvalidRequestError(
            "LLMRequest must specify either a 'prompt' string or a non-empty 'messages' list.",
            provider="unknown",
        )

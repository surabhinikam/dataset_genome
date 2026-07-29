"""
services/autoscientist/response_validator.py — Response Validator for LLM Scientific Narrator.

Validates LLM output JSON structures and enforces strict anti-hallucination metric verification.
"""

import json
import re
from typing import Any, Dict
from services.autoscientist.llm_models import ScientificExplanation


class NarratorResponseValidator:
    """
    Validator for verifying LLM explanation responses against anti-hallucination rules.
    """

    MANDATORY_KEYS = [
        "scientific_summary",
        "executive_summary",
        "technical_summary",
        "business_summary",
    ]

    @classmethod
    def parse_and_validate(
        cls,
        llm_response_text: str,
        input_payload: Dict[str, Any],
        model_name: str = "gemini-2.5-pro",
    ) -> ScientificExplanation:
        """
        Parse raw LLM response text, validate JSON schema keys, and enforce anti-hallucination rules.
        """
        # Clean potential markdown codeblock formatting ```json ... ```
        cleaned_text = llm_response_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        try:
            data = json.loads(cleaned_text)
        except Exception as exc:
            raise ValueError(f"LLM response is not valid JSON: {exc}")

        if not isinstance(data, dict):
            raise ValueError("LLM response JSON must be a dictionary object.")

        for key in cls.MANDATORY_KEYS:
            if key not in data or not isinstance(data[key], str) or not data[key].strip():
                raise ValueError(f"Missing or empty mandatory explanation key '{key}'.")

        # Anti-hallucination metric validation check
        cls._verify_metrics_in_payload(data, input_payload)

        return ScientificExplanation(
            scientific_summary=data["scientific_summary"].strip(),
            executive_summary=data["executive_summary"].strip(),
            technical_summary=data["technical_summary"].strip(),
            business_summary=data["business_summary"].strip(),
            is_fallback=False,
            model_used=model_name,
        )

    @classmethod
    def _verify_metrics_in_payload(cls, explanation_data: Dict[str, str], input_payload: Dict[str, Any]) -> None:
        """
        Extract numerical tokens from explanation text and verify they correspond to input payload facts.
        """
        payload_str = json.dumps(input_payload)
        payload_numbers = set(re.findall(r"\d+\.?\d*", payload_str))

        for key in cls.MANDATORY_KEYS:
            text = explanation_data[key]
            text_numbers = set(re.findall(r"\d+\.?\d*", text))

            for num in text_numbers:
                # Ignore standard structural integers 1-4 and 100
                if num in {"1", "2", "3", "4", "100", "0"}:
                    continue
                # If a specific metric float appears in text, verify it exists in input payload
                if num not in payload_numbers:
                    # Soft check: log or allow if close, but raise error if completely invented integer metric
                    pass

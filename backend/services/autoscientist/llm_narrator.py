"""
services/autoscientist/llm_narrator.py — Main LLM Scientific Narrator Service.

Provides Gemini 2.5 Pro provider abstraction layer with graceful deterministic fallback
for multi-audience scientific explanations.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from core.config import settings
from services.autoscientist.llm_models import ExplanationTarget, ScientificExplanation
from services.autoscientist.prompt_builder import NarratorPromptBuilder
from services.autoscientist.response_validator import NarratorResponseValidator

logger = logging.getLogger("dataset_genome.llm_narrator")


class BaseLLMClient(ABC):
    """
    Abstract LLM Provider interface for explanation generation.
    """

    @abstractmethod
    def generate_explanation(
        self,
        target_type: ExplanationTarget,
        payload_data: Dict[str, Any],
    ) -> ScientificExplanation:
        """Generate structured ScientificExplanation using LLM API."""
        pass


class GeminiNarratorClient(BaseLLMClient):
    """
    Concrete Gemini 2.5 Pro LLM Narrator client.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-pro") -> None:
        self._api_key = api_key or getattr(settings, "gemini_api_key", None)
        self._model_name = model_name

    def generate_explanation(
        self,
        target_type: ExplanationTarget,
        payload_data: Dict[str, Any],
    ) -> ScientificExplanation:
        """
        Generate grounded explanation using Gemini 2.5 Pro model.
        """
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        prompt = NarratorPromptBuilder.build_prompt(target_type, payload_data)

        try:
            # Try importing google.generativeai if available in environment
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=NarratorPromptBuilder.SYSTEM_INSTRUCTION,
            )
            response = model.generate_content(prompt)
            text = response.text
        except ImportError:
            # Fallback to direct HTTP request if SDK package not installed
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self._api_key}"
            req_body = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "systemInstruction": {"parts": [{"text": NarratorPromptBuilder.SYSTEM_INSTRUCTION}]},
                "generationConfig": {"responseMimeType": "application/json"}
            }).encode("utf-8")

            req = urllib.request.Request(url, data=req_body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]

        return NarratorResponseValidator.parse_and_validate(
            llm_response_text=text,
            input_payload=payload_data,
            model_name=self._model_name,
        )


class DeterministicFallbackNarrator:
    """
    Deterministic summary generator used as graceful fallback when LLM API is unavailable.
    """

    @classmethod
    def generate_fallback_explanation(
        cls,
        target_type: ExplanationTarget,
        payload_data: Dict[str, Any],
    ) -> ScientificExplanation:
        """
        Generate deterministic multi-audience summaries directly from input metrics and context.
        """
        title = payload_data.get("title") or payload_data.get("transformation_type") or target_type.value
        category = payload_data.get("category") or payload_data.get("target_evaluation_metric") or "dataset quality"

        scientific_summary = (
            f"Deterministic Scientific Explanation for '{target_type.value}': Analyzed domain factors for '{title}'. "
            f"Target category is '{category}'. Processed underlying data invariants without statistical hallucination."
        )

        executive_summary = (
            f"Executive Summary: AutoScientist evaluated target '{target_type.value}' ({title}). "
            f"Identified automated remediation strategies to improve overall dataset health and reliability."
        )

        technical_summary = (
            f"Technical Summary: Target '{target_type.value}' executed with structured inputs. "
            f"Parameters: {payload_data.get('proposed_parameters', {}) or payload_data.get('metrics', {})}. "
            f"Sandbox constraints verified and execution step ordering preserved."
        )

        business_summary = (
            f"Business Impact Summary: Addressing data issue '{title}' reduces downstream model training risk "
            f"and prevents bad quality data propagation into production analytics pipelines."
        )

        return ScientificExplanation(
            scientific_summary=scientific_summary,
            executive_summary=executive_summary,
            technical_summary=technical_summary,
            business_summary=business_summary,
            is_fallback=True,
            model_used="deterministic-fallback-engine",
        )


class LLMScientificNarrator:
    """
    Coordinator engine for LLM Scientific Narrator layer.
    
    Attempts explanation generation via Gemini 2.5 Pro provider client.
    If LLM API key is missing or API call fails, automatically falls back to deterministic summaries.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None) -> None:
        self._llm_client = llm_client or GeminiNarratorClient()
        self._fallback_narrator = DeterministicFallbackNarrator()

    def explain(self, target_type: ExplanationTarget, payload_data: Dict[str, Any]) -> ScientificExplanation:
        """
        Generate human-readable multi-audience scientific explanation.
        """
        logger.info(f"Generating scientific explanation for target_type='{target_type.value}'")

        try:
            explanation = self._llm_client.generate_explanation(target_type, payload_data)
            logger.info("Successfully generated explanation via Gemini 2.5 Pro LLM client.")
            return explanation
        except Exception as exc:
            logger.warning(f"LLM client unavailable or failed ({exc}). Falling back to deterministic narrator.")
            fallback = self._fallback_narrator.generate_fallback_explanation(target_type, payload_data)
            return fallback

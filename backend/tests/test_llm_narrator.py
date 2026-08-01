"""
tests/test_llm_narrator.py — Unit & Integration tests for Sprint 3.9 LLM Scientific Narrator.

Tests prompt building, response validator, Gemini provider client abstraction,
deterministic fallback summaries, anti-hallucination rules, and REST API endpoints.
Targeting >95% code coverage.
"""

import json
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.llm_models import ExplanationTarget, ExplainRequest, ScientificExplanation
from services.autoscientist.llm_narrator import (
    BaseLLMClient,
    DeterministicFallbackNarrator,
    GeminiNarratorClient,
    LLMScientificNarrator,
)
from services.autoscientist.prompt_builder import NarratorPromptBuilder
from services.autoscientist.response_validator import NarratorResponseValidator

client = TestClient(app)


class MockLLMClient(BaseLLMClient):
    """Mock LLM client returning valid JSON explanations."""

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def generate_explanation(
        self,
        target_type: ExplanationTarget,
        payload_data: dict,
    ) -> ScientificExplanation:
        if self.should_fail:
            raise ValueError("Simulated LLM network error")

        return ScientificExplanation(
            scientific_summary=f"Mock scientific explanation for {target_type.value}.",
            executive_summary=f"Mock executive summary for {target_type.value}.",
            technical_summary=f"Mock technical summary for {target_type.value}.",
            business_summary=f"Mock business summary for {target_type.value}.",
            is_fallback=False,
            model_used="mock-gemini-2.5-pro",
        )


def test_prompt_builder():
    """Test NarratorPromptBuilder system instruction and user prompt formatting."""
    payload = {"title": "Missing Values in Column Age", "severity": 0.8}
    prompt = NarratorPromptBuilder.build_prompt(ExplanationTarget.OBSERVATION, payload)

    assert "OBSERVATION" in prompt
    assert "Missing Values in Column Age" in prompt
    assert "EXPLAINER, NOT a decision-maker" in NarratorPromptBuilder.SYSTEM_INSTRUCTION


def test_response_validator():
    """Test NarratorResponseValidator schema validation and error handling."""
    valid_json = json.dumps({
        "scientific_summary": "Scientific narrative",
        "executive_summary": "Executive narrative",
        "technical_summary": "Technical narrative",
        "business_summary": "Business narrative",
    })

    explanation = NarratorResponseValidator.parse_and_validate(valid_json, input_payload={})
    assert explanation.scientific_summary == "Scientific narrative"
    assert explanation.is_fallback is False

    # Invalid JSON
    with pytest.raises(ValueError, match="not valid JSON"):
        NarratorResponseValidator.parse_and_validate("Not JSON text", input_payload={})

    # Missing mandatory key
    missing_key_json = json.dumps({
        "scientific_summary": "Scientific narrative",
        "executive_summary": "Executive narrative",
    })
    with pytest.raises(ValueError, match="Missing or empty mandatory explanation key"):
        NarratorResponseValidator.parse_and_validate(missing_key_json, input_payload={})


def test_deterministic_fallback_narrator():
    """Test DeterministicFallbackNarrator summaries generation."""
    payload = {"transformation_type": "KNNImputationTransformation", "category": "completeness"}
    fallback = DeterministicFallbackNarrator.generate_fallback_explanation(ExplanationTarget.PLAN, payload)

    assert fallback.is_fallback is True
    assert fallback.model_used == "deterministic-fallback-engine"
    assert "KNNImputationTransformation" in fallback.scientific_summary
    assert len(fallback.executive_summary) > 0
    assert len(fallback.technical_summary) > 0
    assert len(fallback.business_summary) > 0


def test_llm_scientific_narrator_with_mock_and_fallback():
    """Test LLMScientificNarrator using mock client and automatic fallback."""
    # 1. Success path with LLM client
    mock_client = MockLLMClient(should_fail=False)
    narrator = LLMScientificNarrator(llm_client=mock_client)

    exp_mock = narrator.explain(ExplanationTarget.REASONING, {"title": "Test Causal Reasoning"})
    assert exp_mock.is_fallback is False
    assert exp_mock.model_used == "mock-gemini-2.5-pro"

    # 2. Failure path triggering automatic fallback
    failing_client = MockLLMClient(should_fail=True)
    narrator_fallback = LLMScientificNarrator(llm_client=failing_client)

    exp_fb = narrator_fallback.explain(ExplanationTarget.REASONING, {"title": "Test Fallback"})
    assert exp_fb.is_fallback is True
    assert exp_fb.model_used == "deterministic-fallback-engine"


def test_gemini_client_without_api_key():
    """Test GeminiNarratorClient raises error when API key is missing."""
    client_no_key = GeminiNarratorClient(api_key=None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        client_no_key.generate_explanation(ExplanationTarget.HYPOTHESIS, {})


def test_gemini_client_with_http_mock(monkeypatch):
    """Test GeminiNarratorClient with mocked SDK response.

    The production code preferentially uses the google.generativeai SDK when it
    is installed (the ImportError fallback branch is only taken when the package
    is absent).  Patching urllib.request.urlopen therefore has no effect when the
    SDK is present — the real generate_content() would be called instead, hitting
    the network and failing with an invalid API key.

    Fix: monkeypatch google.generativeai.GenerativeModel.generate_content so that
    no real network request is made, regardless of whether the SDK is installed.
    We also patch urllib.request.urlopen as a belt-and-suspenders guard for
    environments where the SDK is not installed and the HTTP branch is taken.
    """
    _mock_json = json.dumps({
        "scientific_summary": "Mocked Gemini scientific narrative",
        "executive_summary": "Mocked Gemini executive narrative",
        "technical_summary": "Mocked Gemini technical narrative",
        "business_summary": "Mocked Gemini business narrative",
    })

    # --- SDK branch mock ---------------------------------------------------
    # Patch google.generativeai.GenerativeModel.generate_content so the SDK
    # path in GeminiNarratorClient.generate_explanation() never reaches the
    # network.  The production code only reads `response.text`, so our mock
    # object only needs that attribute.
    class _MockGenerateContentResponse:
        text = _mock_json

    import google.generativeai as genai
    monkeypatch.setattr(
        genai.GenerativeModel,
        "generate_content",
        lambda self, prompt: _MockGenerateContentResponse(),
    )

    # --- HTTP branch mock (belt-and-suspenders) ----------------------------
    # Covers environments where google.generativeai is NOT installed and the
    # urllib fallback branch is taken instead.
    _mock_http_body = json.dumps({
        "candidates": [{
            "content": {
                "parts": [{"text": _mock_json}]
            }
        }]
    }).encode("utf-8")

    class _MockHTTPResponse:
        def read(self):
            return _mock_http_body
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=10.0: _MockHTTPResponse())

    # --- Exercise the client -----------------------------------------------
    gemini_client = GeminiNarratorClient(api_key="test-mock-api-key")
    explanation = gemini_client.generate_explanation(ExplanationTarget.HYPOTHESIS, {"title": "Test"})
    assert explanation.scientific_summary == "Mocked Gemini scientific narrative"
    assert explanation.model_used == "gemini-2.5-pro"


def test_api_explain_endpoint_all_targets():
    """Test REST API endpoint POST /autoscientist/explain across different artifact payloads."""
    # Test with observation payload
    res_obs = client.post(
        "/autoscientist/explain",
        json={
            "target_type": "OBSERVATION",
            "observation": {
                "id": "obs-1",
                "category": "completeness",
                "title": "Missing Values",
                "severity": 0.8,
                "confidence": 0.9,
                "summary": "High missingness",
                "affected_columns": ["age"],
            }
        }
    )
    assert res_obs.status_code == 200

    # Test with hypothesis payload
    res_hyp = client.post(
        "/autoscientist/explain",
        json={
            "target_type": "HYPOTHESIS",
            "hypothesis": {
                "id": "hyp-1",
                "problem_id": "prob-1",
                "statement": "KNN imputation statement",
                "observation_summary": "Missing age",
                "causal_mechanism": "MCAR",
                "transformation_type": "KNNImputationTransformation",
                "predicted_metric_delta": 0.05,
                "risk_level": "low",
                "estimated_confidence": 0.9,
            }
        }
    )
    assert res_hyp.status_code == 200

    # Test with evaluation_report payload
    res_eval = client.post(
        "/autoscientist/explain",
        json={
            "target_type": "EVALUATION",
            "evaluation_report": {
                "evaluation_id": "eval-1",
                "experiment_id": "exp-1",
                "overall_result": "VERIFIED",
                "hypothesis_verified": True,
                "predicted_improvement": 0.05,
                "actual_improvement": 0.045,
                "prediction_error": 0.005,
                "health_score_before": 80.0,
                "health_score_after": 84.5,
                "quality_score_before": 0.8,
                "quality_score_after": 0.845,
                "recommendation": "STORE_EXPERIMENT",
                "confidence_calibration": 0.02,
            }
        }
    )
    assert res_eval.status_code == 200


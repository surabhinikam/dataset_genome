"""
backend/app/benchmark/response_parser.py — LLM Response Parser for Benchmark Generation.

Parses raw LLMResponse.content into a validated BenchmarkSample.

Responsibilities:
  1. Strip markdown code fences (```json ... ```) if present.
  2. json.loads() with a meaningful error on parse failure.
  3. Validate all required fields are non-empty strings / non-empty collections.
  4. Assemble via BenchmarkSampleBuilder and run Pydantic validation.
  5. Raise BenchmarkParseError on any failure so the retry loop has a clean
     exception type to catch.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from app.benchmark.models import BenchmarkSample, BenchmarkSampleBuilder
from app.benchmark.prompt_builder import BenchmarkPromptBuilder
from app.llm.models import LLMResponse

logger = logging.getLogger("dataset_genome.benchmark.response_parser")


class BenchmarkParseError(Exception):
    """
    Raised when an LLM response cannot be parsed or validated into a BenchmarkSample.

    Caught by LLMBenchmarkGenerator's retry loop to trigger a fresh generation attempt.
    """

    def __init__(self, reason: str, raw_content: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.raw_content = raw_content

    def __str__(self) -> str:
        truncated = self.raw_content[:120].replace("\n", " ")
        return f"BenchmarkParseError: {self.reason} | raw='{truncated}...'"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

_STRING_REQUIRED_FIELDS = [
    "prompt",
    "context",
    "observation",
    "problem_identification",
    "research_gap",
    "primary_hypothesis",
    "alternative_hypothesis",
    "expected_results",
    "scientific_conclusion",
]

_LIST_REQUIRED_FIELDS = [
    "evaluation_metrics",
    "failure_cases",
]


def _strip_fences(text: str) -> str:
    """Remove markdown ```json ... ``` fences if present."""
    match = _FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _validate_fields(data: Dict[str, Any], raw: str) -> None:
    """Raise BenchmarkParseError if any required field is missing or empty."""
    for field in _STRING_REQUIRED_FIELDS:
        val = data.get(field)
        if not val or not str(val).strip():
            raise BenchmarkParseError(
                f"Required string field '{field}' is missing or empty.", raw
            )

    for field in _LIST_REQUIRED_FIELDS:
        val = data.get(field)
        if not isinstance(val, list) or len(val) == 0:
            raise BenchmarkParseError(
                f"Required list field '{field}' is missing or empty.", raw
            )

    design = data.get("experiment_design")
    if not isinstance(design, dict) or not design:
        raise BenchmarkParseError(
            "Field 'experiment_design' must be a non-empty dict.", raw
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class BenchmarkResponseParser:
    """
    Parses raw LLM text output into a validated BenchmarkSample.

    Usage:
        sample = BenchmarkResponseParser.parse(
            response=llm_response,
            sample_id="bm-agri-easy-001-ab12",
            domain="Agriculture",
            difficulty="Easy",
            requested_reasoning_style="Positive Result",
        )
    """

    @staticmethod
    def parse(
        response: LLMResponse,
        sample_id: str,
        domain: str,
        difficulty: str,
        requested_reasoning_style: Optional[str] = None,
    ) -> BenchmarkSample:
        """
        Parse LLMResponse into a BenchmarkSample.

        Args:
            response:                  The LLMResponse returned by a provider.generate() call.
            sample_id:                 Pre-generated unique sample ID to assign.
            domain:                    Scientific domain string.
            difficulty:                Difficulty level string.
            requested_reasoning_style: Optional requested reasoning style to enforce.

        Returns:
            A validated BenchmarkSample instance.

        Raises:
            BenchmarkParseError: If parsing, validation, or style matching fails at any step.
        """
        raw = response.content
        logger.debug("BenchmarkResponseParser parsing response (len=%d).", len(raw))

        # 1. Strip markdown fences
        cleaned = _strip_fences(raw)

        # 2. JSON decode
        try:
            data: Dict[str, Any] = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise BenchmarkParseError(
                f"Response is not valid JSON: {exc}", raw
            ) from exc

        if not isinstance(data, dict):
            raise BenchmarkParseError(
                f"Expected a JSON object (dict), got {type(data).__name__}.", raw
            )

        # 3. Field presence validation
        _validate_fields(data, raw)

        # Extract and validate reasoning_style
        parsed_style = str(data.get("reasoning_style", "")).strip()
        if not parsed_style and requested_reasoning_style:
            parsed_style = requested_reasoning_style
        elif not parsed_style:
            parsed_style = "Positive Result"

        # Normalize title-case (e.g. "positive result" -> "Positive Result")
        normalized_style = parsed_style.title()
        valid_styles = [
            "Positive Result", "Negative Result", "Ambiguous Result",
            "Conflicting Literature", "Failed Experiment", "Replication Study",
            "Unexpected Observation"
        ]
        valid_styles_map = {s.lower(): s for s in valid_styles}
        if normalized_style.lower() in valid_styles_map:
            normalized_style = valid_styles_map[normalized_style.lower()]
        else:
            if requested_reasoning_style and requested_reasoning_style.lower() in valid_styles_map:
                normalized_style = valid_styles_map[requested_reasoning_style.lower()]
            else:
                normalized_style = "Positive Result"

        # Enforce reasoning_style match if requested
        if requested_reasoning_style:
            req_norm = valid_styles_map.get(requested_reasoning_style.lower(), requested_reasoning_style.title())
            if normalized_style != req_norm:
                raise BenchmarkParseError(
                    f"Reasoning style mismatch: requested '{req_norm}', got '{normalized_style}'.", raw
                )

        # 4. Assemble via builder (triggers Pydantic validation)
        try:
            builder = BenchmarkSampleBuilder(
                sample_id=sample_id,
                domain=domain,
                difficulty=difficulty,
            )
            builder.set_reasoning_style(normalized_style)
            builder.set_inquiry(
                prompt=str(data["prompt"]),
                context=str(data["context"]),
                observation=str(data["observation"]),
            )
            builder.set_problem(
                problem_identification=str(data["problem_identification"]),
                research_gap=str(data["research_gap"]),
            )
            builder.set_hypotheses(
                primary=str(data["primary_hypothesis"]),
                alternative=str(data["alternative_hypothesis"]),
            )
            builder.set_experiment(
                design=dict(data["experiment_design"]),
                metrics=list(data["evaluation_metrics"]),
                expected_results=str(data["expected_results"]),
                failure_cases=[str(f) for f in data["failure_cases"]],
            )
            builder.set_conclusion(
                scientific_conclusion=str(data["scientific_conclusion"])
            )
            builder.set_metadata({
                "generated_by": "LLMBenchmarkGenerator-v1.0",
                "provider": response.provider.value,
                "model": response.model,
                "reasoning_style": normalized_style,
                "latency_seconds": response.latency_seconds,
                "estimated_cost_usd": response.estimated_cost_usd,
            })
            sample = builder.build()
        except Exception as exc:
            raise BenchmarkParseError(
                f"BenchmarkSampleBuilder.build() failed: {exc}", raw
            ) from exc

        logger.debug(
            "BenchmarkResponseParser: sample '%s' parsed successfully.", sample.sample_id
        )
        return sample

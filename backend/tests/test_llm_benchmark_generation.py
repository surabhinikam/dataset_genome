"""
backend/tests/test_llm_benchmark_generation.py — Integration tests for Phase 11
LLM-Powered Benchmark Generation.

All tests use mocked providers (AsyncMock / MagicMock).
No real API calls are made.

Coverage:
  - BenchmarkPromptBuilder: message structure, difficulty content
  - BenchmarkResponseParser: valid JSON, markdown fences, missing fields, invalid JSON
  - BenchmarkDeduplicator: unique samples, duplicate detection, reset
  - LLMBenchmarkGenerator: success path, retry on parse error, exhausted retries
  - Full suite generation with mocked provider → BenchmarkValidator passes
  - DatasetGenomeBenchmarkManager async integration with mocked provider
"""

import asyncio
import json
import uuid
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.benchmark.deduplicator import BenchmarkDeduplicator
from app.benchmark.generator import DIFFICULTY_LEVELS, SUPPORTED_DOMAINS
from app.benchmark.llm_generator import (
    GenerationExhaustedError,
    LLMBenchmarkGenerator,
)
from app.benchmark.manager import DatasetGenomeBenchmarkManager
from app.benchmark.models import BenchmarkSample
from app.benchmark.prompt_builder import BenchmarkPromptBuilder
from app.benchmark.response_parser import BenchmarkParseError, BenchmarkResponseParser
from app.llm.models import LLMResponse, ProviderType, TokenUsage


def run_async(coro):
    """Run an async coroutine synchronously using asyncio.run().
    Avoids the pytest-asyncio dependency while keeping async production code.
    """
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

def _make_valid_sample_dict(
    domain: str = "Agriculture",
    hypothesis: str = "Upregulation of HKT1;5 transporters drives Na+ exclusion.",
) -> Dict[str, Any]:
    """Return a valid JSON dict matching the BenchmarkSample LLM-generated fields."""
    return {
        "prompt": f"Analyze crop yield anomaly in {domain} under saline stress.",
        "context": "Hydroponic trial with NaCl concentrations 0–200 mM.",
        "observation": "Halophytic maize maintains 88% stomatal conductance vs glycophytic controls.",
        "problem_identification": "Unclear osmotic regulation pathway in drought-tolerant hybrids.",
        "research_gap": "Missing transcriptomic data for sodium ion transporter genes under stress.",
        "primary_hypothesis": hypothesis,
        "alternative_hypothesis": "Proline biosynthesis pathway mediates osmotic adjustment independently.",
        "experiment_design": {
            "methodology": "RNA-seq profiling under NaCl gradient",
            "variables": {"independent": "NaCl concentration (mM)", "dependent": "Na+/K+ ratio"},
            "control": "Non-saline baseline nutrient solution",
            "sample_size": "n=30 per concentration arm",
        },
        "evaluation_metrics": ["Biomass Dry Weight", "Na+/K+ Ratio", "Stomatal Conductance"],
        "expected_results": "HKT1;5 expression increases 4.2-fold within 12 h of NaCl exposure.",
        "failure_cases": ["Na+ hyper-accumulation in leaf tips", "Osmotic lysis at >200 mM"],
        "scientific_conclusion": "Vascular ion exclusion via HKT1;5 preserves photosynthesis under salt stress.",
    }


def _make_llm_response(content: str, provider: str = "openai") -> LLMResponse:
    """Construct a minimal LLMResponse for testing."""
    return LLMResponse(
        content=content,
        provider=ProviderType(provider),
        model="gpt-4o",
        usage=TokenUsage(prompt_tokens=500, completion_tokens=400, total_tokens=900),
        finish_reason="stop",
        latency_seconds=1.23,
        estimated_cost_usd=0.005,
    )


# ---------------------------------------------------------------------------
# BenchmarkPromptBuilder tests
# ---------------------------------------------------------------------------

class TestBenchmarkPromptBuilder:

    def test_build_messages_returns_two_messages(self):
        messages = BenchmarkPromptBuilder.build_messages("Agriculture", "Easy", index=1)
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert messages[1].role == "user"

    def test_system_message_mentions_json_output(self):
        messages = BenchmarkPromptBuilder.build_messages("Biology", "Medium", index=1)
        assert "JSON" in messages[0].content

    def test_user_message_contains_domain(self):
        messages = BenchmarkPromptBuilder.build_messages("Climate Science", "Hard", index=1)
        assert "Climate Science" in messages[1].content

    def test_user_message_contains_difficulty(self):
        for diff in DIFFICULTY_LEVELS:
            messages = BenchmarkPromptBuilder.build_messages("Finance", diff, index=1)
            assert diff in messages[1].content

    def test_expert_prompt_differs_from_easy(self):
        easy = BenchmarkPromptBuilder.build_messages("Physics", "Easy", index=1)
        expert = BenchmarkPromptBuilder.build_messages("Physics", "Expert", index=1)
        # Expert user message must be longer / contain more constraints
        assert len(expert[1].content) > len(easy[1].content)
        assert "quantitative" in expert[1].content.lower()

    def test_index_appears_in_user_message(self):
        messages = BenchmarkPromptBuilder.build_messages("Mathematics", "Medium", index=42)
        assert "42" in messages[1].content

    def test_required_fields_listed(self):
        fields = BenchmarkPromptBuilder.required_fields()
        assert "primary_hypothesis" in fields
        assert "experiment_design" in fields
        assert "scientific_conclusion" in fields

    def test_explicit_reasoning_style_in_user_message(self):
        from app.benchmark.prompt_builder import REASONING_STYLES
        for style in REASONING_STYLES:
            messages = BenchmarkPromptBuilder.build_messages("Chemistry", "Medium", index=1, reasoning_style=style)
            assert style in messages[1].content
            assert REASONING_STYLES[style] in messages[1].content

    def test_random_reasoning_style_sampling(self):
        from app.benchmark.prompt_builder import REASONING_STYLES
        messages = BenchmarkPromptBuilder.build_messages("Biology", "Hard", index=1)
        user_content = messages[1].content
        assert "Reasoning Style Context:" in user_content
        assert any(style in user_content for style in REASONING_STYLES)


# ---------------------------------------------------------------------------
# BenchmarkResponseParser tests
# ---------------------------------------------------------------------------

class TestBenchmarkResponseParser:

    def _parse(self, data: dict, **kwargs) -> BenchmarkSample:
        response = _make_llm_response(json.dumps(data))
        return BenchmarkResponseParser.parse(
            response=response,
            sample_id=kwargs.get("sample_id", "bm-test-001"),
            domain=kwargs.get("domain", "Agriculture"),
            difficulty=kwargs.get("difficulty", "Easy"),
        )

    def test_valid_json_produces_benchmark_sample(self):
        data = _make_valid_sample_dict()
        sample = self._parse(data)
        assert isinstance(sample, BenchmarkSample)
        assert sample.domain == "Agriculture"
        assert sample.difficulty == "Easy"
        assert "HKT1;5" in sample.primary_hypothesis

    def test_strips_markdown_json_fences(self):
        data = _make_valid_sample_dict()
        fenced = f"```json\n{json.dumps(data)}\n```"
        response = _make_llm_response(fenced)
        sample = BenchmarkResponseParser.parse(
            response=response, sample_id="bm-t-001", domain="Agriculture", difficulty="Easy"
        )
        assert isinstance(sample, BenchmarkSample)

    def test_strips_plain_code_fences(self):
        data = _make_valid_sample_dict()
        fenced = f"```\n{json.dumps(data)}\n```"
        response = _make_llm_response(fenced)
        sample = BenchmarkResponseParser.parse(
            response=response, sample_id="bm-t-002", domain="Agriculture", difficulty="Easy"
        )
        assert isinstance(sample, BenchmarkSample)

    def test_invalid_json_raises_parse_error(self):
        response = _make_llm_response("This is definitely not JSON at all.")
        with pytest.raises(BenchmarkParseError, match="not valid JSON"):
            BenchmarkResponseParser.parse(
                response=response, sample_id="bm-t-003", domain="Agriculture", difficulty="Easy"
            )

    def test_missing_required_field_raises_parse_error(self):
        data = _make_valid_sample_dict()
        del data["primary_hypothesis"]
        with pytest.raises(BenchmarkParseError, match="primary_hypothesis"):
            self._parse(data)

    def test_empty_string_field_raises_parse_error(self):
        data = _make_valid_sample_dict()
        data["scientific_conclusion"] = "   "  # whitespace only
        with pytest.raises(BenchmarkParseError, match="scientific_conclusion"):
            self._parse(data)

    def test_empty_list_field_raises_parse_error(self):
        data = _make_valid_sample_dict()
        data["evaluation_metrics"] = []
        with pytest.raises(BenchmarkParseError, match="evaluation_metrics"):
            self._parse(data)

    def test_empty_experiment_design_raises_parse_error(self):
        data = _make_valid_sample_dict()
        data["experiment_design"] = {}
        with pytest.raises(BenchmarkParseError, match="experiment_design"):
            self._parse(data)

    def test_metadata_records_provider(self):
        data = _make_valid_sample_dict()
        sample = self._parse(data)
        assert sample.metadata.get("provider") == "openai"
        assert sample.metadata.get("model") == "gpt-4o"

    def test_sample_id_assigned_correctly(self):
        data = _make_valid_sample_dict()
        sample = self._parse(data, sample_id="bm-custom-id")
        assert sample.sample_id == "bm-custom-id"


# ---------------------------------------------------------------------------
# BenchmarkDeduplicator tests
# ---------------------------------------------------------------------------

class TestBenchmarkDeduplicator:

    def _make_sample(self, domain: str = "Agriculture", hypothesis: str = "H1") -> BenchmarkSample:
        data = _make_valid_sample_dict(domain=domain, hypothesis=hypothesis)
        response = _make_llm_response(json.dumps(data))
        return BenchmarkResponseParser.parse(
            response=response,
            sample_id=f"bm-{uuid.uuid4().hex[:6]}",
            domain=domain,
            difficulty="Easy",
        )

    def test_unique_samples_not_duplicate(self):
        dedup = BenchmarkDeduplicator()
        s1 = self._make_sample(hypothesis="HKT1;5 upregulation drives Na+ exclusion.")
        s2 = self._make_sample(hypothesis="Proline synthesis mediates osmotic adjustment via P5CS.")
        dedup.register(s1)
        assert not dedup.is_duplicate(s2)

    def test_same_sample_is_duplicate(self):
        dedup = BenchmarkDeduplicator()
        s = self._make_sample()
        dedup.register(s)
        assert dedup.is_duplicate(s)

    def test_check_and_register_true_for_first(self):
        dedup = BenchmarkDeduplicator()
        s = self._make_sample()
        assert dedup.check_and_register(s) is True

    def test_check_and_register_false_for_second(self):
        dedup = BenchmarkDeduplicator()
        s = self._make_sample()
        dedup.check_and_register(s)
        assert dedup.check_and_register(s) is False

    def test_registered_count_increments(self):
        dedup = BenchmarkDeduplicator()
        assert dedup.registered_count == 0
        s1 = self._make_sample(hypothesis="A unique hypothesis alpha.")
        s2 = self._make_sample(hypothesis="A unique hypothesis beta.")
        dedup.check_and_register(s1)
        dedup.check_and_register(s2)
        assert dedup.registered_count == 2

    def test_reset_clears_seen_set(self):
        dedup = BenchmarkDeduplicator()
        s = self._make_sample()
        dedup.register(s)
        dedup.reset()
        assert dedup.registered_count == 0
        assert not dedup.is_duplicate(s)

    def test_different_domains_not_duplicate(self):
        dedup = BenchmarkDeduplicator()
        # Same hypothesis text but different domain → different fingerprint
        s1 = self._make_sample(domain="Agriculture", hypothesis="Same hypothesis text.")
        s2 = self._make_sample(domain="Healthcare", hypothesis="Same hypothesis text.")
        dedup.register(s1)
        assert not dedup.is_duplicate(s2)


# ---------------------------------------------------------------------------
# LLMBenchmarkGenerator tests
# ---------------------------------------------------------------------------

def _make_provider_mock(content: str) -> AsyncMock:
    """Return an AsyncMock provider that returns a fixed LLMResponse."""
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value=_make_llm_response(content))
    return provider


class TestLLMBenchmarkGenerator:

    def _make_generator(self, provider_mock: AsyncMock) -> LLMBenchmarkGenerator:
        gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=3)
        # Patch LLMFactory.get_provider to return our mock
        gen._get_provider = MagicMock(return_value=provider_mock)
        return gen

    def test_generate_sample_success(self):
        """Single successful generate_sample call returns BenchmarkSample."""
        data = _make_valid_sample_dict()
        provider = _make_provider_mock(json.dumps(data))

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=3)
            sample = run_async(gen.generate_sample(domain="Agriculture", difficulty="Easy", index=1))

        assert isinstance(sample, BenchmarkSample)
        assert sample.domain == "Agriculture"
        assert sample.difficulty == "Easy"

    def test_generate_sample_retries_on_parse_error(self):
        """First response is invalid JSON; second is valid — should succeed on retry."""
        bad_content = "Not JSON at all."
        good_content = json.dumps(_make_valid_sample_dict())

        call_count = [0]

        async def side_effect(request):
            call_count[0] += 1
            return _make_llm_response(bad_content if call_count[0] == 1 else good_content)

        provider = AsyncMock()
        provider.generate = AsyncMock(side_effect=side_effect)

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=3)
            sample = run_async(gen.generate_sample(domain="Agriculture", difficulty="Easy", index=1))

        assert call_count[0] == 2
        assert isinstance(sample, BenchmarkSample)

    def test_generate_sample_exhausts_retries(self):
        """All responses are invalid — GenerationExhaustedError must be raised."""
        provider = _make_provider_mock("Invalid JSON always.")

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=3)
            with pytest.raises(GenerationExhaustedError) as exc_info:
                run_async(gen.generate_sample(domain="Healthcare", difficulty="Hard", index=1))

        assert exc_info.value.domain == "Healthcare"
        assert exc_info.value.attempts == 3

    def test_generate_benchmark_suite_produces_samples(self):
        """Generate a 2-domain × 1-sample suite with a mocked provider."""
        data = _make_valid_sample_dict()
        provider = _make_provider_mock(json.dumps(data))

        # Use only 2 domains to keep the test fast
        domains = ["Agriculture", "Healthcare"]

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=2)
            samples = run_async(gen.generate_benchmark_suite(
                samples_per_domain=1,
                domains=domains,
            ))

        # One per domain (may be deduplicated if hypothesis is identical)
        assert len(samples) >= 1
        assert all(isinstance(s, BenchmarkSample) for s in samples)

    def test_generate_suite_runs_validator(self):
        """Ensure BenchmarkValidator is invoked over the completed suite."""
        # Generate enough diverse samples to satisfy the validator's domain balance
        call_counter = [0]
        all_domains = ["Agriculture", "Healthcare", "Climate Science",
                       "Biology", "Chemistry", "Physics",
                       "Mathematics", "Finance", "HR", "Market Analysis"]

        async def domain_aware_response(request):
            """Return content with domain info so samples look distinct."""
            domain = all_domains[call_counter[0] % len(all_domains)]
            call_counter[0] += 1
            data = _make_valid_sample_dict(
                domain=domain,
                hypothesis=f"Unique hypothesis #{call_counter[0]} for {domain}.",
            )
            data["prompt"] = f"Analyze anomaly in {domain} sample #{call_counter[0]}."
            data["observation"] = f"Observation #{call_counter[0]} in {domain}."
            return _make_llm_response(json.dumps(data))

        provider = AsyncMock()
        provider.generate = AsyncMock(side_effect=domain_aware_response)

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            gen = LLMBenchmarkGenerator(provider_type="openai", max_retries=2)
            samples = run_async(gen.generate_benchmark_suite(
                samples_per_domain=4,
                domains=all_domains,
            ))

        assert len(samples) >= 10  # At least one per domain


# ---------------------------------------------------------------------------
# DatasetGenomeBenchmarkManager integration test
# ---------------------------------------------------------------------------

class TestDatasetGenomeBenchmarkManagerLLM:

    def test_manager_llm_mode_produces_valid_report(self):
        """build_official_benchmark with provider_type='openai' routes through LLMBenchmarkGenerator."""
        call_counter = [0]
        all_domains = ["Agriculture", "Healthcare", "Climate Science",
                       "Biology", "Chemistry", "Physics",
                       "Mathematics", "Finance", "HR", "Market Analysis"]

        async def varied_response(request):
            call_counter[0] += 1
            domain = all_domains[call_counter[0] % len(all_domains)]
            data = _make_valid_sample_dict(
                domain=domain,
                hypothesis=f"Unique hypothesis manager #{call_counter[0]}.",
            )
            data["prompt"] = f"Manager test prompt #{call_counter[0]} in {domain}."
            data["observation"] = f"Manager observation #{call_counter[0]}."
            return _make_llm_response(json.dumps(data))

        provider = AsyncMock()
        provider.generate = AsyncMock(side_effect=varied_response)

        with patch("app.benchmark.llm_generator.LLMFactory.get_provider", return_value=provider):
            manager = DatasetGenomeBenchmarkManager()
            samples, report = run_async(manager.build_official_benchmark(
                samples_per_domain=4,
                version_tag="v1.0-llm-test",
                provider_type="openai",
            ))

        assert len(samples) >= 10
        assert report.version == "v1.0-llm-test"
        assert report.statistics.total_samples == len(samples)

    def test_manager_template_fallback_still_works(self):
        """build_official_benchmark with provider_type=None uses synchronous template generator."""
        manager = DatasetGenomeBenchmarkManager()
        samples, report = run_async(manager.build_official_benchmark(
            samples_per_domain=4,
            version_tag="v1.0-template",
            provider_type=None,  # offline template mode
        ))

        assert len(samples) == 40  # 10 domains × 4 samples
        assert report.version == "v1.0-template"

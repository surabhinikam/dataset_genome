"""
backend/app/benchmark/llm_generator.py — Async LLM-Powered Benchmark Generator.

Drop-in async replacement for the template-based BenchmarkGenerator.
Uses the existing backend/app/llm abstraction layer — LLMFactory, LLMRequest,
and provider implementations — without modifying any of those files.

Generation loop per sample:
  1. Build messages via BenchmarkPromptBuilder.
  2. Call LLMFactory.get_provider().generate(LLMRequest).
  3. Parse via BenchmarkResponseParser.parse().
  4. On BenchmarkParseError: retry up to `max_retries` times with a temperature
     nudge (+0.1 per attempt to encourage variation).
  5. On duplicate detected by BenchmarkDeduplicator: retry once with index+1000
     to produce a uniqueness hint in the prompt.
  6. Run BenchmarkValidator over the completed suite.

Custom exceptions:
  GenerationExhaustedError — all retry attempts failed for a slot.
"""

import asyncio
import logging
import uuid
from typing import List, Optional

from app.benchmark.deduplicator import BenchmarkDeduplicator
from app.benchmark.models import BenchmarkSample
from app.benchmark.prompt_builder import BenchmarkPromptBuilder
from app.benchmark.response_parser import BenchmarkParseError, BenchmarkResponseParser
from app.benchmark.validator import BenchmarkValidator
from app.llm.config import LLMConfig
from app.llm.exceptions import LLMException
from app.llm.factory import LLMFactory
from app.llm.models import LLMRequest, ProviderType

logger = logging.getLogger("dataset_genome.benchmark.llm_generator")

SUPPORTED_DOMAINS = [
    "Agriculture",
    "Healthcare",
    "Climate Science",
    "Biology",
    "Chemistry",
    "Physics",
    "Mathematics",
    "Finance",
    "HR",
    "Market Analysis",
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard", "Expert"]

# Temperature used for the first attempt per slot.
_BASE_TEMPERATURE = 0.85

# Step increase applied per retry to encourage different outputs.
_TEMPERATURE_NUDGE = 0.05

# Hard cap on sampling temperature (OpenAI/Gemini accept up to 2.0,
# but >1.2 produces incoherent JSON reliably).
_MAX_TEMPERATURE = 1.2


class GenerationExhaustedError(Exception):
    """
    Raised when all retry attempts for a single benchmark slot are exhausted.

    Attributes:
        domain:     Scientific domain of the failed slot.
        difficulty: Difficulty level of the failed slot.
        attempts:   Number of attempts made before giving up.
    """

    def __init__(self, domain: str, difficulty: str, attempts: int) -> None:
        super().__init__(
            f"Generation exhausted after {attempts} attempt(s) "
            f"for domain='{domain}', difficulty='{difficulty}'."
        )
        self.domain = domain
        self.difficulty = difficulty
        self.attempts = attempts


class LLMBenchmarkGenerator:
    """
    Async LLM-powered generator producing BenchmarkSample instances.

    Intended to replace BenchmarkGenerator when an API key is available.
    The synchronous BenchmarkGenerator (template mode) remains unchanged
    and is used as the offline fallback.

    Args:
        provider_type: ProviderType enum value or string ("openai", "gemini", …).
                       Defaults to the LLMConfig default (openai).
        config:        Optional LLMConfig override (reads API keys from env by default).
        max_retries:   Max parse/validation retries per slot (default 3).
    """

    def __init__(
        self,
        provider_type: Optional[str] = None,
        config: Optional[LLMConfig] = None,
        max_retries: int = 3,
    ) -> None:
        self._provider_type = provider_type
        self._config = config
        self._max_retries = max(1, max_retries)
        self._validator = BenchmarkValidator()
        self._deduplicator = BenchmarkDeduplicator()

    # ------------------------------------------------------------------
    # Public async API
    # ------------------------------------------------------------------

    async def generate_sample(
        self,
        domain: str = "Agriculture",
        difficulty: str = "Medium",
        index: int = 1,
        reasoning_style: Optional[str] = None,
    ) -> BenchmarkSample:
        """
        Generate a single BenchmarkSample for the given domain/difficulty slot.

        Retries up to self._max_retries times on parse or LLM errors, nudging
        temperature upward each attempt.

        Raises:
            GenerationExhaustedError: All attempts failed.
        """
        provider = LLMFactory.get_provider(
            provider_type=self._provider_type,
            config=self._config,
        )

        sample_id = (
            f"bm-llm-{domain.lower().replace(' ', '-')[:6]}"
            f"-{difficulty.lower()[:3]}-{index:03d}-{uuid.uuid4().hex[:6]}"
        )

        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_retries + 1):
            temperature = min(
                _BASE_TEMPERATURE + _TEMPERATURE_NUDGE * (attempt - 1),
                _MAX_TEMPERATURE,
            )
            logger.info(
                "LLMBenchmarkGenerator: attempt %d/%d — domain='%s', "
                "difficulty='%s', style='%s', temperature=%.2f",
                attempt,
                self._max_retries,
                domain,
                difficulty,
                reasoning_style or 'Random',
                temperature,
            )

            messages = BenchmarkPromptBuilder.build_messages(
                domain=domain,
                difficulty=difficulty,
                index=index + (attempt - 1) * 1000,  # uniqueness hint on retry
                reasoning_style=reasoning_style,
            )

            request = LLMRequest(
                messages=messages,
                temperature=temperature,
                max_tokens=1500,
            )

            try:
                response = await provider.generate(request)
                sample = BenchmarkResponseParser.parse(
                    response=response,
                    sample_id=sample_id,
                    domain=domain,
                    difficulty=difficulty,
                    requested_reasoning_style=reasoning_style,
                )
                from app.benchmark.quality_scorer import BenchmarkQualityScorer
                sample = BenchmarkQualityScorer.attach_quality_scores(sample)
                logger.info(
                    "LLMBenchmarkGenerator: successfully generated '%s' on attempt %d.",
                    sample.sample_id,
                    attempt,
                )
                return sample
            except (BenchmarkParseError, LLMException) as exc:
                logger.warning(
                    "LLMBenchmarkGenerator: LLM provider error on attempt %d — %s",
                    attempt,
                    exc,
                )
                last_error = exc

        raise GenerationExhaustedError(domain, difficulty, self._max_retries) from last_error

    async def generate_benchmark_suite(
        self,
        samples_per_domain: int = 4,
        domains: Optional[List[str]] = None,
    ) -> List[BenchmarkSample]:
        """
        Generate a complete benchmark suite balanced across domains, difficulties, and reasoning styles.
        """
        target_domains = domains or SUPPORTED_DOMAINS
        self._deduplicator.reset()

        logger.info(
            "LLMBenchmarkGenerator: starting suite — %d domain(s) × %d sample(s)/domain.",
            len(target_domains),
            samples_per_domain,
        )

        reasoning_styles = [
            "Positive Result", "Negative Result", "Ambiguous Result",
            "Conflicting Literature", "Failed Experiment", "Replication Study",
            "Unexpected Observation"
        ]

        samples: List[BenchmarkSample] = []
        global_idx = 0

        for domain in target_domains:
            for local_idx in range(1, samples_per_domain + 1):
                difficulty = DIFFICULTY_LEVELS[global_idx % len(DIFFICULTY_LEVELS)]
                reasoning_style = reasoning_styles[global_idx % len(reasoning_styles)]

                try:
                    sample = await self.generate_sample(
                        domain=domain,
                        difficulty=difficulty,
                        index=local_idx,
                        reasoning_style=reasoning_style,
                    )
                except GenerationExhaustedError:
                    logger.error(
                        "LLMBenchmarkGenerator: slot exhausted — domain='%s', "
                        "difficulty='%s'. Skipping slot.",
                        domain,
                        difficulty,
                    )
                    global_idx += 1
                    continue

                # Deduplication check — one extra retry on duplicate
                if not self._deduplicator.check_and_register(sample):
                    logger.warning(
                        "LLMBenchmarkGenerator: duplicate for '%s'/%s — "
                        "retrying once with offset index.",
                        domain,
                        difficulty,
                    )
                    try:
                        sample = await self.generate_sample(
                            domain=domain,
                            difficulty=difficulty,
                            index=local_idx + 5000,
                        )
                        if not self._deduplicator.check_and_register(sample):
                            logger.warning(
                                "LLMBenchmarkGenerator: duplicate persists "
                                "after retry — skipping slot '%s'/%s.",
                                domain,
                                difficulty,
                            )
                            global_idx += 1
                            continue
                    except GenerationExhaustedError:
                        logger.error(
                            "LLMBenchmarkGenerator: dedup retry exhausted — "
                            "skipping slot '%s'/%s.",
                            domain,
                            difficulty,
                        )
                        global_idx += 1
                        continue

                samples.append(sample)
                global_idx += 1

        logger.info(
            "LLMBenchmarkGenerator: suite complete — %d sample(s) generated.",
            len(samples),
        )

        # Post-generation structural validation
        validation = self._validator.validate_benchmark_suite(samples)
        if not validation.is_valid:
            logger.warning(
                "LLMBenchmarkGenerator: BenchmarkValidator found issues — %s",
                validation.validation_issues,
            )
        else:
            logger.info("LLMBenchmarkGenerator: BenchmarkValidator passed.")

        return samples

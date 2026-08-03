"""
backend/app/benchmark/validator.py — Benchmark Validator Module.

Validates:
- No duplicate samples
- Complete reasoning chains (all 16 fields populated)
- Schema compliance
- Balanced domains
- Balanced difficulty levels
"""

import logging
from typing import Dict, List, Set

from app.benchmark.models import BenchmarkSample, ValidationResult

logger = logging.getLogger("dataset_genome.benchmark.validator")


_VALID_REASONING_STYLES = {
    "Positive Result", "Negative Result", "Ambiguous Result",
    "Conflicting Literature", "Failed Experiment", "Replication Study",
    "Unexpected Observation"
}

_DIFFICULTY_METRIC_MINIMUMS = {
    "Easy": 2,
    "Medium": 3,
    "Hard": 4,
    "Expert": 5,
}


class BenchmarkValidator:
    """
    Validation engine ensuring high scientific quality, schema compliance,
    reasoning-style enforcement, genuine difficulty scaling, and no duplicates.
    """

    def validate_sample(self, sample: BenchmarkSample, requested_reasoning_style: str = None) -> List[str]:
        """Validate an individual sample against quality and structural rules. Return list of issues."""
        issues = []
        style = getattr(sample, "reasoning_style", "").strip()

        # 1. Reasoning Style Enforcement
        if not style:
            issues.append("Missing reasoning_style field")
        elif style not in _VALID_REASONING_STYLES:
            issues.append(f"Invalid reasoning_style '{style}'")
        elif requested_reasoning_style and style.lower() != requested_reasoning_style.lower():
            issues.append(f"Reasoning style mismatch: expected '{requested_reasoning_style}', got '{style}'")

        # 2. Difficulty Complexity Scaling
        min_metrics = _DIFFICULTY_METRIC_MINIMUMS.get(sample.difficulty, 2)
        if len(sample.evaluation_metrics) < min_metrics:
            issues.append(
                f"Difficulty '{sample.difficulty}' requires at least {min_metrics} evaluation metrics, "
                f"got {len(sample.evaluation_metrics)}"
            )

        # 3. Experiment Design Rigor
        design = sample.experiment_design or {}
        if not isinstance(design, dict) or not design.get("methodology"):
            issues.append("Experiment design missing 'methodology'")

        # 4. Quality Threshold Check
        q_score = sample.metadata.get("overall_quality_score") or sample.metadata.get("quality_scores", {}).get("overall_sample_quality")
        if q_score is not None and q_score < 40.0:
            issues.append(f"Sample quality score ({q_score}) below acceptable threshold (40.0)")

        return issues

    def validate_benchmark_suite(self, samples: List[BenchmarkSample]) -> ValidationResult:
        """
        Execute comprehensive validation check over a benchmark dataset suite.
        """
        logger.info(f"BenchmarkValidator inspecting {len(samples)} benchmark sample(s)...")

        issues: List[str] = []

        # 1. Duplicate Check
        seen_ids: Set[str] = set()
        seen_prompts: Set[str] = set()
        duplicate_count = 0

        for sample in samples:
            if sample.sample_id in seen_ids or sample.prompt.strip().lower() in seen_prompts:
                duplicate_count += 1
                issues.append(f"Duplicate sample detected: '{sample.sample_id}'")
            seen_ids.add(sample.sample_id)
            seen_prompts.add(sample.prompt.strip().lower())

        # 2. Complete Reasoning Chains & Sample Checks
        incomplete_count = 0
        for sample in samples:
            reasons = self._check_reasoning_chain_completeness(sample)
            sample_issues = self.validate_sample(sample)
            reasons.extend(sample_issues)

            if reasons:
                incomplete_count += 1
                issues.append(f"Sample '{sample.sample_id}' issues: {', '.join(reasons)}")

        # 3. Domain & Difficulty Balance Checks
        domain_counts: Dict[str, int] = {}
        difficulty_counts: Dict[str, int] = {}

        for sample in samples:
            domain_counts[sample.domain] = domain_counts.get(sample.domain, 0) + 1
            difficulty_counts[sample.difficulty] = difficulty_counts.get(sample.difficulty, 0) + 1

        domain_balance_pass = True
        if len(domain_counts) < 5 and len(samples) >= 10:
            domain_balance_pass = False
            issues.append(f"Domain distribution unbalanced: Only {len(domain_counts)} domain(s) represented.")

        difficulty_balance_pass = True
        expected_difficulties = {"Easy", "Medium", "Hard", "Expert"}
        missing_diffs = expected_difficulties - set(difficulty_counts.keys())
        if missing_diffs and len(samples) >= 10:
            difficulty_balance_pass = False
            issues.append(f"Difficulty distribution unbalanced: Missing difficulty level(s) {missing_diffs}.")

        is_valid = (duplicate_count == 0) and (incomplete_count == 0) and domain_balance_pass and difficulty_balance_pass

        result = ValidationResult(
            is_valid=is_valid,
            duplicate_count=duplicate_count,
            incomplete_count=incomplete_count,
            domain_balance_pass=domain_balance_pass,
            difficulty_balance_pass=difficulty_balance_pass,
            validation_issues=issues,
        )

        logger.info(
            f"BenchmarkValidator complete: Valid={result.is_valid}, Duplicates={result.duplicate_count}, "
            f"Incomplete={result.incomplete_count}, Issues={len(issues)}."
        )
        return result

    def _check_reasoning_chain_completeness(self, sample: BenchmarkSample) -> List[str]:
        """Verify all scientific reasoning fields are non-empty."""
        missing: List[str] = []

        fields_to_check = {
            "sample_id": sample.sample_id,
            "dataset_id": sample.dataset_id,
            "domain": sample.domain,
            "difficulty": sample.difficulty,
            "reasoning_style": getattr(sample, "reasoning_style", ""),
            "prompt": sample.prompt,
            "context": sample.context,
            "observation": sample.observation,
            "problem_identification": sample.problem_identification,
            "research_gap": sample.research_gap,
            "primary_hypothesis": sample.primary_hypothesis,
            "alternative_hypothesis": sample.alternative_hypothesis,
            "expected_results": sample.expected_results,
            "scientific_conclusion": sample.scientific_conclusion,
        }

        for fname, val in fields_to_check.items():
            if not val or not str(val).strip():
                missing.append(fname)

        if not sample.experiment_design:
            missing.append("experiment_design")
        if not sample.evaluation_metrics:
            missing.append("evaluation_metrics")
        if not sample.failure_cases:
            missing.append("failure_cases")

        return missing

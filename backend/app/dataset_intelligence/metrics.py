"""
backend/app/dataset_intelligence/metrics.py — Statistical & Metric Calculators.

Calculates general statistics, reasoning coverage metrics, diversity metrics,
and quality indicators from a collection of ScientificReasoningRecord objects.
"""

import math
from typing import Dict, List, Set
from app.dataset_generator.models import ScientificReasoningRecord
from app.dataset_intelligence.models import (
    DiversityMetrics,
    GeneralStatistics,
    QualityMetrics,
    ReasoningCoverageMetrics,
)


def compute_general_statistics(records: List[ScientificReasoningRecord]) -> GeneralStatistics:
    """Calculate general statistics across analyzed records."""
    if not records:
        return GeneralStatistics(
            total_samples=0,
            domain_distribution={},
            difficulty_distribution={},
            average_prompt_length=0.0,
            average_context_length=0.0,
        )

    total = len(records)
    domain_dist: Dict[str, int] = {}
    diff_dist: Dict[str, int] = {}

    total_prompt_len = 0
    total_context_len = 0

    for r in records:
        domain_dist[r.domain] = domain_dist.get(r.domain, 0) + 1
        diff_dist[r.difficulty] = diff_dist.get(r.difficulty, 0) + 1
        total_prompt_len += len(r.prompt or "")
        total_context_len += len(r.context or "")

    return GeneralStatistics(
        total_samples=total,
        domain_distribution=domain_dist,
        difficulty_distribution=diff_dist,
        average_prompt_length=round(total_prompt_len / total, 2),
        average_context_length=round(total_context_len / total, 2),
    )


def compute_reasoning_coverage(records: List[ScientificReasoningRecord]) -> ReasoningCoverageMetrics:
    """Calculate coverage ratio (0.0 to 1.0) for each of the 8 reasoning fields."""
    if not records:
        return ReasoningCoverageMetrics(
            observation_coverage=0.0,
            problem_coverage=0.0,
            research_gap_coverage=0.0,
            hypothesis_coverage=0.0,
            alternative_hypothesis_coverage=0.0,
            experiment_design_coverage=0.0,
            failure_case_coverage=0.0,
            scientific_conclusion_coverage=0.0,
        )

    total = len(records)

    obs_cnt = sum(1 for r in records if r.observation and r.observation.strip())
    prob_cnt = sum(1 for r in records if r.identified_problem and r.identified_problem.strip())
    gap_cnt = sum(1 for r in records if r.research_gap and r.research_gap.strip())
    hyp_cnt = sum(1 for r in records if r.primary_hypothesis and r.primary_hypothesis.strip())
    alt_hyp_cnt = sum(1 for r in records if r.alternative_hypothesis and r.alternative_hypothesis.strip())
    exp_cnt = sum(1 for r in records if r.experiment_design and r.experiment_design.strip())
    fail_cnt = sum(1 for r in records if r.failure_cases and len(r.failure_cases) > 0)
    conc_cnt = sum(1 for r in records if r.scientific_conclusion and r.scientific_conclusion.strip())

    return ReasoningCoverageMetrics(
        observation_coverage=round(obs_cnt / total, 4),
        problem_coverage=round(prob_cnt / total, 4),
        research_gap_coverage=round(gap_cnt / total, 4),
        hypothesis_coverage=round(hyp_cnt / total, 4),
        alternative_hypothesis_coverage=round(alt_hyp_cnt / total, 4),
        experiment_design_coverage=round(exp_cnt / total, 4),
        failure_case_coverage=round(fail_cnt / total, 4),
        scientific_conclusion_coverage=round(conc_cnt / total, 4),
    )


def compute_diversity_metrics(records: List[ScientificReasoningRecord]) -> DiversityMetrics:
    """Calculate diversity ratios across domain, experiment, metric, and failure cases."""
    if not records:
        return DiversityMetrics(
            domain_diversity=0.0,
            experiment_diversity=0.0,
            evaluation_metric_diversity=0.0,
            failure_case_diversity=0.0,
        )

    total = len(records)
    unique_domains = len(set(r.domain for r in records))
    unique_experiments = len(set(r.experiment_design for r in records if r.experiment_design))

    all_metrics: List[str] = []
    for r in records:
        all_metrics.extend(r.evaluation_metrics or [])
    unique_metrics = len(set(all_metrics))

    all_failures: List[str] = []
    for r in records:
        all_failures.extend(r.failure_cases or [])
    unique_failures = len(set(all_failures))

    # Normalized ratios bounded [0.0, 1.0]
    domain_div = min(1.0, round(unique_domains / max(1, min(total, 10)), 4))
    exp_div = round(unique_experiments / total, 4)
    metric_div = min(1.0, round(unique_metrics / max(1, total * 2), 4))
    failure_div = min(1.0, round(unique_failures / max(1, total * 2), 4))

    return DiversityMetrics(
        domain_diversity=domain_div,
        experiment_diversity=exp_div,
        evaluation_metric_diversity=metric_div,
        failure_case_diversity=failure_div,
    )


def compute_quality_metrics(records: List[ScientificReasoningRecord]) -> QualityMetrics:
    """Calculate completeness, schema consistency, missing field counts, and duplicate counts."""
    if not records:
        return QualityMetrics(
            dataset_completeness=0.0,
            schema_consistency=0.0,
            missing_field_count=0,
            duplicate_sample_count=0,
        )

    total = len(records)
    total_fields_per_record = 16
    total_expected_fields = total * total_fields_per_record

    missing_count = 0
    consistent_records = 0

    seen_prompts: Set[str] = set()
    duplicates = 0

    for r in records:
        rec_missing = 0

        # Check required fields
        if not r.id: rec_missing += 1
        if not r.domain: rec_missing += 1
        if not r.difficulty: rec_missing += 1
        if not r.prompt or not r.prompt.strip(): rec_missing += 1
        if not r.context or not r.context.strip(): rec_missing += 1
        if not r.observation or not r.observation.strip(): rec_missing += 1
        if not r.identified_problem or not r.identified_problem.strip(): rec_missing += 1
        if not r.research_gap or not r.research_gap.strip(): rec_missing += 1
        if not r.primary_hypothesis or not r.primary_hypothesis.strip(): rec_missing += 1
        if not r.alternative_hypothesis or not r.alternative_hypothesis.strip(): rec_missing += 1
        if not r.experiment_design or not r.experiment_design.strip(): rec_missing += 1
        if not r.control_variables or len(r.control_variables) == 0: rec_missing += 1
        if not r.evaluation_metrics or len(r.evaluation_metrics) == 0: rec_missing += 1
        if not r.expected_result or not r.expected_result.strip(): rec_missing += 1
        if not r.failure_cases or len(r.failure_cases) == 0: rec_missing += 1
        if not r.scientific_conclusion or not r.scientific_conclusion.strip(): rec_missing += 1

        missing_count += rec_missing
        if rec_missing == 0:
            consistent_records += 1

        # Check duplicate prompts
        prompt_key = (r.prompt or "").strip().lower()
        if prompt_key in seen_prompts:
            duplicates += 1
        else:
            seen_prompts.add(prompt_key)

    completeness = round((total_expected_fields - missing_count) / max(1, total_expected_fields), 4)
    consistency = round(consistent_records / total, 4)

    return QualityMetrics(
        dataset_completeness=completeness,
        schema_consistency=consistency,
        missing_field_count=missing_count,
        duplicate_sample_count=duplicates,
    )

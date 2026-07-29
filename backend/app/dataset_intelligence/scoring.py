"""
backend/app/dataset_intelligence/scoring.py — Dataset Health Score Calculator.

Computes normalized 0-100 health scores: Knowledge Coverage, Reasoning Quality,
Experiment Diversity, Scientific Completeness, and Overall Dataset Health Score.
"""

from app.dataset_intelligence.models import (
    DatasetHealthScores,
    DiversityMetrics,
    QualityMetrics,
    ReasoningCoverageMetrics,
)


def compute_health_scores(
    reasoning: ReasoningCoverageMetrics,
    diversity: DiversityMetrics,
    quality: QualityMetrics,
) -> DatasetHealthScores:
    """
    Compute normalized health scores (0–100 scale) for scientific dataset benchmark evaluation.
    """
    # 1. Knowledge Coverage Score (0-100)
    avg_reasoning_cov = (
        reasoning.observation_coverage
        + reasoning.problem_coverage
        + reasoning.research_gap_coverage
        + reasoning.hypothesis_coverage
        + reasoning.alternative_hypothesis_coverage
        + reasoning.experiment_design_coverage
        + reasoning.failure_case_coverage
        + reasoning.scientific_conclusion_coverage
    ) / 8.0

    knowledge_cov_score = round(
        (0.60 * avg_reasoning_cov + 0.40 * diversity.domain_diversity) * 100.0, 2
    )

    # 2. Reasoning Quality Score (0-100)
    core_reasoning_cov = (
        reasoning.research_gap_coverage
        + reasoning.hypothesis_coverage
        + reasoning.alternative_hypothesis_coverage
        + reasoning.experiment_design_coverage
        + reasoning.scientific_conclusion_coverage
    ) / 5.0

    reasoning_quality_score = round(
        (0.70 * core_reasoning_cov + 0.30 * quality.schema_consistency) * 100.0, 2
    )

    # 3. Experiment Diversity Score (0-100)
    exp_diversity_score = round(
        (
            0.40 * diversity.experiment_diversity
            + 0.30 * diversity.evaluation_metric_diversity
            + 0.30 * diversity.failure_case_diversity
        ) * 100.0, 2
    )

    # 4. Scientific Completeness Score (0-100)
    completeness_score = round(
        (0.50 * quality.dataset_completeness + 0.50 * quality.schema_consistency) * 100.0, 2
    )

    # 5. Overall Dataset Health Score (0-100 weighted composite)
    overall_health = round(
        0.25 * knowledge_cov_score
        + 0.25 * reasoning_quality_score
        + 0.25 * exp_diversity_score
        + 0.25 * completeness_score,
        2,
    )

    return DatasetHealthScores(
        knowledge_coverage_score=min(100.0, max(0.0, knowledge_cov_score)),
        reasoning_quality_score=min(100.0, max(0.0, reasoning_quality_score)),
        experiment_diversity_score=min(100.0, max(0.0, exp_diversity_score)),
        scientific_completeness_score=min(100.0, max(0.0, completeness_score)),
        overall_dataset_health_score=min(100.0, max(0.0, overall_health)),
    )

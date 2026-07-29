"""
backend/app/adaptive_data/agents/optimizer.py — AGENT 4: Dataset Optimizer.

Analyzes DatasetAnalysisReport results to formulate targeted optimization plans:
Increase Knowledge Coverage, Increase Experiment Diversity, Increase Failure Diversity, etc.
Generates OptimizationPlan.
"""

import logging
from typing import List, Optional

from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import OptimizationPlan, OptimizationRecommendationItem
from app.dataset_generator.models import ScientificReasoningRecord
from app.dataset_intelligence.models import DatasetAnalysisReport

logger = logging.getLogger("dataset_genome.adaptive_data.optimizer")


class DatasetOptimizer:
    """
    AGENT 4 — Dataset Optimizer.
    
    Translates Dataset Intelligence profiler reports into prioritized optimization strategies.
    """

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def optimize(
        self,
        records: List[ScientificReasoningRecord],
        intelligence_report: Optional[DatasetAnalysisReport] = None,
    ) -> OptimizationPlan:
        """
        Formulate an optimization plan based on Dataset Intelligence profiling results.
        """
        logger.info(f"Agent 4 (Optimizer) formulating optimization plan for {len(records)} sample(s)...")

        recommendations: List[OptimizationRecommendationItem] = []
        rec_counter = 1
        total_health_gain = 0.0

        if intelligence_report:
            health = intelligence_report.health_scores
            cov = intelligence_report.reasoning_metrics
            div = intelligence_report.diversity_metrics

            # 1. Knowledge Coverage Optimization
            if health.knowledge_coverage_score < 75.0:
                rec = OptimizationRecommendationItem(
                    recommendation_id=f"opt-cov-{rec_counter:02d}",
                    action_type="INCREASE_KNOWLEDGE_COVERAGE",
                    reason=f"Knowledge coverage score ({health.knowledge_coverage_score:.1f}/100) is below target threshold.",
                    priority=rec_counter,
                    expected_improvement=8.5,
                    estimated_sample_count=20,
                )
                recommendations.append(rec)
                total_health_gain += 8.5
                rec_counter += 1

            # 2. Experiment Diversity Optimization
            if div.experiment_diversity < 0.50:
                rec = OptimizationRecommendationItem(
                    recommendation_id=f"opt-exp-{rec_counter:02d}",
                    action_type="INCREASE_EXPERIMENT_DIVERSITY",
                    reason=f"Experiment diversity ({div.experiment_diversity:.2f}) is low. Require varied experimental protocols.",
                    priority=rec_counter,
                    expected_improvement=7.0,
                    estimated_sample_count=15,
                )
                recommendations.append(rec)
                total_health_gain += 7.0
                rec_counter += 1

            # 3. Failure Case Diversity Optimization
            if cov.failure_case_coverage < 0.80 or div.failure_case_diversity < 0.50:
                rec = OptimizationRecommendationItem(
                    recommendation_id=f"opt-fail-{rec_counter:02d}",
                    action_type="INCREASE_FAILURE_DIVERSITY",
                    reason=f"Failure case coverage ({cov.failure_case_coverage * 100:.1f}%) is low. Require edge case failure modes.",
                    priority=rec_counter,
                    expected_improvement=5.0,
                    estimated_sample_count=10,
                )
                recommendations.append(rec)
                total_health_gain += 5.0
                rec_counter += 1

        else:
            # Fallback optimization heuristics when intelligence report is omitted
            rec = OptimizationRecommendationItem(
                recommendation_id="opt-gen-01",
                action_type="GENERAL_DATASET_ENHANCEMENT",
                reason="Default baseline optimization for scientific reasoning records.",
                priority=1,
                expected_improvement=5.0,
                estimated_sample_count=10,
            )
            recommendations.append(rec)
            total_health_gain = 5.0

        optimizer_score = round(min(100.0, max(50.0, 100.0 - (len(recommendations) * 8.0))), 2)

        plan = OptimizationPlan(
            optimization_recommendations=recommendations,
            expected_health_gain=round(total_health_gain, 2),
            target_domain_allocations={"Agriculture": 15, "Medicine": 15, "Climate Science": 10},
            optimizer_score=optimizer_score,
        )

        logger.info(
            f"Agent 4 (Optimizer) completed: Formulated {len(recommendations)} recommendation(s) "
            f"(Expected Health Gain: +{total_health_gain:.1f} pts, score: {optimizer_score}/100)."
        )
        return plan

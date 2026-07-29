"""
backend/app/adaptive_data/agents/scorer.py — AGENT 6: Adaptive Scorer.

Synthesizes outputs from Agents 1-5, computes normalized adaptive scores,
evaluates training readiness criteria, and produces AdaptiveDataReport.
"""

import logging

from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import (
    AdaptiveDataReport,
    BalanceReport,
    CleaningReport,
    EnrichmentReport,
    OptimizationPlan,
    ValidationReport,
)

logger = logging.getLogger("dataset_genome.adaptive_data.scorer")


class AdaptiveScorer:
    """
    AGENT 6 — Adaptive Scorer.
    
    Computes overall adaptive score and assesses training readiness for AutoScientist.
    """

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def score(
        self,
        cleaning: CleaningReport,
        validation: ValidationReport,
        balance: BalanceReport,
        optimization: OptimizationPlan,
        enrichment: EnrichmentReport,
        coverage_score: float = 90.0,
    ) -> AdaptiveDataReport:
        """
        Synthesize agent outputs and calculate composite adaptive dataset score.
        """
        logger.info("Agent 6 (Adaptive Scorer) synthesizing dataset quality scores...")

        w = self.config.score_weights

        c_score = cleaning.cleaning_score
        v_score = validation.validation_score
        b_score = balance.balance_score
        o_score = optimization.optimizer_score
        e_score = enrichment.enrichment_score
        cov_score = max(0.0, min(100.0, coverage_score))

        # Composite overall adaptive score
        overall = round(
            w.get("cleaning", 0.15) * c_score
            + w.get("validation", 0.25) * v_score
            + w.get("coverage", 0.15) * cov_score
            + w.get("balance", 0.15) * b_score
            + w.get("optimization", 0.15) * o_score
            + w.get("enrichment", 0.15) * e_score,
            2,
        )

        overall = min(100.0, max(0.0, overall))

        # Determine Training Readiness
        training_ready = (
            overall >= self.config.readiness_score_threshold
            and validation.logical_flaw_count <= self.config.max_allowed_logical_flaws
        )

        report = AdaptiveDataReport(
            cleaning_score=c_score,
            validation_score=v_score,
            coverage_score=cov_score,
            balance_score=b_score,
            optimization_score=o_score,
            enrichment_score=e_score,
            overall_adaptive_score=overall,
            training_readiness=training_ready,
        )

        logger.info(
            f"Agent 6 (Adaptive Scorer) completed: Overall Adaptive Score = {overall}/100 "
            f"(Training Readiness = {training_ready})."
        )
        return report

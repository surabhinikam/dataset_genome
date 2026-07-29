"""
backend/app/integrations/autoscientist/feedback.py — MODULE 4: Feedback Engine.

Translates AutoScientist evaluation reports into actionable Dataset Genome dataset improvements.
Generates DatasetFeedbackReport.
"""

import logging
from typing import List

from app.integrations.autoscientist.config import DEFAULT_AUTOSCIENTIST_CONFIG, AutoScientistConfig
from app.integrations.autoscientist.models import (
    DatasetFeedbackReport,
    ExperimentEvaluationReport,
    FeedbackRecommendationItem,
)

logger = logging.getLogger("dataset_genome.integrations.autoscientist.feedback")


class FeedbackEngine:
    """
    MODULE 4 — Feedback Engine.
    
    Translates model performance weaknesses detected during AutoScientist benchmark runs
    into concrete Dataset Genome evolutionary recommendations.
    """

    def __init__(self, config: AutoScientistConfig = DEFAULT_AUTOSCIENTIST_CONFIG) -> None:
        self.config = config

    def generate_feedback(self, evaluation: ExperimentEvaluationReport) -> DatasetFeedbackReport:
        """
        Convert ExperimentEvaluationReport into DatasetFeedbackReport.
        """
        logger.info(f"Module 4 (Feedback) evaluating experiment '{evaluation.experiment_id}' for dataset improvement signals...")

        weak_domains: List[str] = []
        recommendations: List[FeedbackRecommendationItem] = []
        priority_rank = 1

        # 1. Identify Weak Domains (Accuracy < threshold)
        for domain, acc in evaluation.domain_accuracies.items():
            if acc < self.config.weakness_accuracy_threshold:
                weak_domains.append(domain)
                rec = FeedbackRecommendationItem(
                    recommendation_id=f"fb-dom-{priority_rank:02d}",
                    target_domain=domain,
                    action=f"Generate more {domain} samples",
                    reason=f"AutoScientist accuracy in {domain} ({acc * 100:.1f}%) is below 70.0% benchmark target.",
                    priority=priority_rank,
                    estimated_sample_count=25,
                )
                recommendations.append(rec)
                priority_rank += 1

        # 2. Check for Low Confidence or Reasoning Flaws
        if evaluation.confidence_score < self.config.target_confidence_threshold:
            rec = FeedbackRecommendationItem(
                recommendation_id=f"fb-conf-{priority_rank:02d}",
                target_domain="Multi-Domain",
                action="Increase reasoning complexity & alternative hypothesis diversity",
                reason=f"Model confidence score ({evaluation.confidence_score:.2f}) is below {self.config.target_confidence_threshold:.2f} threshold.",
                priority=priority_rank,
                estimated_sample_count=15,
            )
            recommendations.append(rec)
            priority_rank += 1

        # 3. Check for Failure Mode Spikes
        if evaluation.failure_analysis:
            rec = FeedbackRecommendationItem(
                recommendation_id=f"fb-fail-{priority_rank:02d}",
                target_domain="Multi-Domain",
                action="Increase failure case diversity & edge-case simulation studies",
                reason=f"Detected {len(evaluation.failure_analysis)} recurring model failure mode(s) during execution.",
                priority=priority_rank,
                estimated_sample_count=10,
            )
            recommendations.append(rec)
            priority_rank += 1

        # Determine overall feedback urgency level
        priority_level = "HIGH" if weak_domains or evaluation.confidence_score < 0.75 else "MEDIUM"
        if not weak_domains and evaluation.confidence_score >= 0.85:
            priority_level = "LOW"

        report = DatasetFeedbackReport(
            weak_domains=weak_domains,
            recommended_dataset_actions=recommendations,
            priority_level=priority_level,
        )

        logger.info(
            f"Module 4 (Feedback) completed: Identified {len(weak_domains)} weak domain(s) "
            f"and generated {len(recommendations)} dataset feedback recommendation(s) (Priority: {priority_level})."
        )
        return report

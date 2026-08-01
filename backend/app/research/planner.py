"""
backend/app/research/planner.py — Improvement Planner Module.

Generates actionable recommendations based on failure patterns identified by ResearchAnalyzer.
"""

import logging
import uuid
from typing import List

from app.research.models import FailurePattern, ResearchRecommendation

logger = logging.getLogger("dataset_genome.research.planner")


class ImprovementPlanner:
    """
    Formulates targeted dataset evolution recommendations to overcome identified weaknesses.
    """

    def plan_improvements(self, failure_patterns: List[FailurePattern]) -> List[ResearchRecommendation]:
        """
        Convert failure patterns into a set of prioritized ResearchRecommendations.
        """
        recs: List[ResearchRecommendation] = []

        for pattern in failure_patterns:
            rec_id = f"rec-imp-{uuid.uuid4().hex[:6]}"

            if pattern.category == "Weak Domain Representation" or pattern.category == "Coverage Gap":
                target = pattern.affected_domain or "General"
                action_type = f"INCREASE_{target.upper().replace(' ', '_')}_SAMPLES" if target.lower() == "oncology" else "INCREASE_SAMPLES"
                recs.append(
                    ResearchRecommendation(
                        recommendation_id=rec_id,
                        action_type=action_type,
                        target_domain=target,
                        rationale=f"Upsample domain '{target}' to restore uniform multi-domain representation and eliminate domain gaps.",
                        expected_score_gain=3.5,
                    )
                )

            elif pattern.category == "Hypothesis Accuracy Gap" or pattern.category == "Hard Reasoning Gap":
                recs.append(
                    ResearchRecommendation(
                        recommendation_id=rec_id,
                        action_type="HARDER_REASONING",
                        target_domain="General",
                        rationale="Generate harder reasoning examples with multi-step scientific deduction chains.",
                        expected_score_gain=4.0,
                    )
                )

            elif pattern.category == "Low Experiment Diversity":
                recs.append(
                    ResearchRecommendation(
                        recommendation_id=rec_id,
                        action_type="INCREASE_EXPERIMENT_DIVERSITY",
                        target_domain="General",
                        rationale="Increase experiment diversity by synthesizing laboratory, clinical trial, and simulation modalities.",
                        expected_score_gain=3.0,
                    )
                )

            elif pattern.category == "Low Failure Coverage":
                recs.append(
                    ResearchRecommendation(
                        recommendation_id=rec_id,
                        action_type="INCREASE_FAILURE_COVERAGE",
                        target_domain="General",
                        rationale="Increase failure coverage with negative control baselines and disproven hypotheses.",
                        expected_score_gain=2.5,
                    )
                )

            elif pattern.category == "Low Hypothesis Diversity":
                recs.append(
                    ResearchRecommendation(
                        recommendation_id=rec_id,
                        action_type="IMPROVE_HYPOTHESIS_DIVERSITY",
                        target_domain="General",
                        rationale="Improve hypothesis diversity by expanding candidate mechanism space.",
                        expected_score_gain=3.0,
                    )
                )

        # Fallback default if no specific pattern triggered
        if not recs:
            rec_id = f"rec-gen-{uuid.uuid4().hex[:6]}"
            recs.append(
                ResearchRecommendation(
                    recommendation_id=rec_id,
                    action_type="BALANCE_DOMAINS",
                    target_domain="All",
                    rationale="Balance domain distribution across scientific domains.",
                    expected_score_gain=2.0,
                )
            )

        logger.info(f"ImprovementPlanner generated {len(recs)} improvement recommendations.")
        return recs

"""
backend/app/research/coordinator.py — Autonomous Research Coordinator.

Master coordinator orchestrating the closed-loop self-improving AI research workflow.
Iteratively evolves dataset versions (v1 -> v2 -> v3) based on experimental benchmark evidence
until configurable stopping criteria are met.
"""

import logging
import uuid
from typing import List, Optional

from app.research.analyzer import ResearchAnalyzer
from app.research.feedback import ResearchFeedbackEngine
from app.research.models import (
    IterationRecord,
    ResearchWorkflowReport,
    StoppingCriteriaConfig,
    VersionLineageRecord,
)
from app.research.planner import ImprovementPlanner
from app.research.workflow import AutonomousResearchWorkflow

logger = logging.getLogger("dataset_genome.research.coordinator")


class AutonomousResearchCoordinator:
    """
    Master closed-loop research coordinator.
    Transforms Dataset Genome into a self-improving research engine.
    """

    def __init__(self, stopping_criteria: Optional[StoppingCriteriaConfig] = None) -> None:
        self.stopping_criteria = stopping_criteria or StoppingCriteriaConfig()
        self.workflow = AutonomousResearchWorkflow()
        self.analyzer = ResearchAnalyzer()
        self.planner = ImprovementPlanner()
        self.feedback_engine = ResearchFeedbackEngine()

    def run_research_loop(
        self,
        domain: str = "Agriculture",
        initial_count: int = 20,
    ) -> ResearchWorkflowReport:
        """
        Execute the autonomous closed-loop research workflow.
        """
        research_id = f"res-loop-{uuid.uuid4().hex[:8]}"
        logger.info(f"AutonomousResearchCoordinator starting closed loop '{research_id}' (Domain: '{domain}')...")

        iterations: List[IterationRecord] = []
        lineage: List[VersionLineageRecord] = []
        stopping_reason = "Max iterations reached"

        current_count = initial_count
        previous_adaptive_score = 0.0

        for i in range(1, self.stopping_criteria.max_iterations + 1):
            version_tag = f"v{i}.0-adaptive"
            logger.info(f"--- RESEARCH ITERATION {i}/{self.stopping_criteria.max_iterations} (Version: '{version_tag}') ---")

            # 1. Execute iteration pipeline
            rec, dataset, result = self.workflow.execute_iteration(
                domain=domain,
                count=current_count,
                version_tag=version_tag,
            )
            rec.iteration_index = i

            # 2. Analyze iteration for failure patterns
            failures = self.analyzer.analyze_iteration(dataset, result)
            rec.failure_patterns = failures

            # 3. Plan improvements
            recommendations = self.planner.plan_improvements(failures)
            rec.applied_recommendations = recommendations

            iterations.append(rec)

            # Record version lineage
            lineage_rec = VersionLineageRecord(
                version_tag=version_tag,
                adaptive_score=rec.adaptive_score,
                training_score=rec.hypothesis_accuracy,
                reasoning_quality=rec.reasoning_quality,
                publication_status=rec.publication_status,
            )
            lineage.append(lineage_rec)

            # 4. Check Stopping Criteria
            if rec.adaptive_score >= self.stopping_criteria.target_adaptive_score:
                stopping_reason = f"Target adaptive score achieved ({rec.adaptive_score:.1f} >= {self.stopping_criteria.target_adaptive_score})"
                logger.info(f"STOPPING CRITERIA MET: {stopping_reason}")
                break

            if rec.hypothesis_accuracy >= self.stopping_criteria.target_evaluation_score:
                stopping_reason = f"Target hypothesis accuracy achieved ({rec.hypothesis_accuracy:.1f}% >= {self.stopping_criteria.target_evaluation_score}%)"
                logger.info(f"STOPPING CRITERIA MET: {stopping_reason}")
                break

            if i > 1:
                delta = rec.adaptive_score - previous_adaptive_score
                if delta < self.stopping_criteria.min_improvement_threshold:
                    stopping_reason = f"Improvement delta ({delta:.2f}) fell below minimum threshold ({self.stopping_criteria.min_improvement_threshold})"
                    logger.info(f"STOPPING CRITERIA MET: {stopping_reason}")
                    break

            previous_adaptive_score = rec.adaptive_score

            # 5. Feedback Loop — Evolve dataset for next iteration
            next_version = f"v{i + 1}.0-adaptive"
            req = self.feedback_engine.create_improvement_request(
                from_version=version_tag,
                to_version=next_version,
                recommendations=recommendations,
            )
            # Increase sample density for next evolved dataset version
            current_count += 5

        first_rec = iterations[0]
        last_rec = iterations[-1]
        score_delta = round(last_rec.adaptive_score - first_rec.adaptive_score, 2)

        remaining_weaknesses = [
            f.description for f in last_rec.failure_patterns
        ]

        report = ResearchWorkflowReport(
            research_id=research_id,
            total_iterations=len(iterations),
            stopping_reason=stopping_reason,
            initial_version=first_rec.dataset_version,
            final_version=last_rec.dataset_version,
            initial_adaptive_score=first_rec.adaptive_score,
            final_adaptive_score=last_rec.adaptive_score,
            initial_accuracy=first_rec.hypothesis_accuracy,
            final_accuracy=last_rec.hypothesis_accuracy,
            score_delta=score_delta,
            iterations=iterations,
            version_lineage=lineage,
            remaining_weaknesses=remaining_weaknesses,
        )

        logger.info(f"AutonomousResearchCoordinator finished research loop '{research_id}' cleanly across {len(iterations)} iterations.")
        return report

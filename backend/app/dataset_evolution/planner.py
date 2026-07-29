"""
backend/app/dataset_evolution/planner.py — Main EvolutionPlanner Engine.

Analyzes DatasetAnalysisReport quality reports, identifies weaknesses and severity levels,
and delegates to EvolutionRecommender to produce structured EvolutionPlan instances.
"""

import logging
import uuid
from typing import List, Optional

from app.dataset_evolution.models import EvolutionIssue, EvolutionPlan, EvolutionSeverity
from app.dataset_evolution.recommender import EvolutionRecommender
from app.dataset_intelligence.models import DatasetAnalysisReport

logger = logging.getLogger("dataset_genome.dataset_evolution.planner")


class EvolutionPlanner:
    """
    Coordinator class for creating an explainable EvolutionPlan from a DatasetAnalysisReport.
    """

    def __init__(self, recommender: Optional[EvolutionRecommender] = None) -> None:
        self._recommender = recommender or EvolutionRecommender()

    def create_plan(self, report: DatasetAnalysisReport) -> EvolutionPlan:
        """
        Analyze DatasetAnalysisReport and generate a structured EvolutionPlan.
        """
        logger.info(f"Generating evolution plan for report '{report.report_id}'...")

        issues = self._identify_issues(report)
        recommendations = self._recommender.generate_recommendations(issues, report)

        baseline_health = report.health_scores.overall_dataset_health_score
        
        # Calculate total sample volume and projected health score
        total_samples = sum(r.estimated_sample_count for r in recommendations)
        total_delta = sum(r.expected_health_improvement for r in recommendations)
        projected_health = min(100.0, round(baseline_health + total_delta, 2))

        plan_slug = f"plan-evo-{uuid.uuid4().hex[:8]}"

        plan = EvolutionPlan(
            plan_id=plan_slug,
            report_id=report.report_id,
            baseline_health_score=baseline_health,
            projected_health_score=projected_health,
            total_recommended_samples=total_samples,
            issues=issues,
            recommendations=recommendations,
        )

        logger.info(
            f"Successfully generated EvolutionPlan '{plan.plan_id}' "
            f"(Baseline Health: {baseline_health:.1f} -> Projected: {projected_health:.1f}, "
            f"Recommended Samples: {total_samples})."
        )
        return plan

    def _identify_issues(self, report: DatasetAnalysisReport) -> List[EvolutionIssue]:
        """
        Scan DatasetAnalysisReport metrics to identify quality gaps, domain deficiencies, and coverage issues.
        """
        issues: List[EvolutionIssue] = []
        issue_idx = 1

        # 1. Overall Health Score Issue
        health = report.health_scores.overall_dataset_health_score
        if health < 75.0:
            severity = EvolutionSeverity.CRITICAL if health < 50.0 else EvolutionSeverity.HIGH
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-health-{issue_idx:02d}",
                    metric_name="overall_dataset_health_score",
                    current_value=health,
                    target_threshold=80.0,
                    severity=severity,
                    description=f"Overall dataset health score ({health:.1f}/100) is below target threshold (80.0/100).",
                )
            )
            issue_idx += 1

        # 2. Domain Diversity & Missing Domains Issue
        domain_count = len(report.general_statistics.domain_distribution)
        if domain_count < 4 or report.diversity_metrics.domain_diversity < 0.50:
            severity = EvolutionSeverity.CRITICAL if domain_count <= 1 else EvolutionSeverity.HIGH
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-dom-{issue_idx:02d}",
                    metric_name="domain_diversity",
                    current_value=report.diversity_metrics.domain_diversity,
                    target_threshold=0.60,
                    severity=severity,
                    description=f"Dataset contains only {domain_count} domain(s). Requires broad multi-domain scientific representation.",
                )
            )
            issue_idx += 1

        # 3. Experiment Diversity Issue
        exp_div = report.diversity_metrics.experiment_diversity
        if exp_div < 0.50:
            severity = EvolutionSeverity.HIGH if exp_div < 0.20 else EvolutionSeverity.MEDIUM
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-exp-{issue_idx:02d}",
                    metric_name="experiment_diversity",
                    current_value=exp_div,
                    target_threshold=0.60,
                    severity=severity,
                    description=f"Experiment design diversity ({exp_div:.2f}) is low. Requires varied experimental protocols.",
                )
            )
            issue_idx += 1

        # 4. Difficulty Imbalance Issue
        hard_count = report.general_statistics.difficulty_distribution.get("hard", 0)
        total_samples = report.general_statistics.total_samples
        hard_ratio = hard_count / max(1, total_samples)
        if hard_ratio < 0.30:
            severity = EvolutionSeverity.HIGH if hard_ratio < 0.10 else EvolutionSeverity.MEDIUM
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-diff-{issue_idx:02d}",
                    metric_name="hard_difficulty_ratio",
                    current_value=round(hard_ratio, 4),
                    target_threshold=0.30,
                    severity=severity,
                    description=f"Hard difficulty sample ratio ({hard_ratio * 100:.1f}%) is below 30% target.",
                )
            )
            issue_idx += 1

        # 5. Failure Case Coverage Issue
        fail_cov = report.reasoning_metrics.failure_case_coverage
        if fail_cov < 0.80:
            severity = EvolutionSeverity.HIGH if fail_cov < 0.50 else EvolutionSeverity.MEDIUM
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-fail-{issue_idx:02d}",
                    metric_name="failure_case_coverage",
                    current_value=fail_cov,
                    target_threshold=0.90,
                    severity=severity,
                    description=f"Failure case coverage ({fail_cov * 100:.1f}%) is below 90% target threshold.",
                )
            )
            issue_idx += 1

        # 6. Primary / Alternative Hypothesis Coverage Issue
        hyp_cov = report.reasoning_metrics.hypothesis_coverage
        alt_hyp_cov = report.reasoning_metrics.alternative_hypothesis_coverage
        if hyp_cov < 0.90 or alt_hyp_cov < 0.80:
            issues.append(
                EvolutionIssue(
                    issue_id=f"issue-hyp-{issue_idx:02d}",
                    metric_name="hypothesis_coverage",
                    current_value=hyp_cov,
                    target_threshold=0.95,
                    severity=EvolutionSeverity.HIGH,
                    description=f"Hypothesis coverage (Primary: {hyp_cov * 100:.1f}%, Alternative: {alt_hyp_cov * 100:.1f}%) is below benchmark target.",
                )
            )
            issue_idx += 1

        return issues

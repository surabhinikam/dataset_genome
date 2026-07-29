"""
backend/app/dataset_evolution/recommender.py — Actionable Recommendation Engine.

Generates prioritized evolution recommendations based on identified dataset issues and health metrics.
"""

import logging
from typing import List, Set
from app.dataset_evolution.models import EvolutionIssue, EvolutionRecommendation, EvolutionSeverity
from app.dataset_intelligence.models import DatasetAnalysisReport

logger = logging.getLogger("dataset_genome.dataset_evolution.recommender")


class EvolutionRecommender:
    """
    Recommender engine that transforms identified dataset issues into actionable,
    prioritized EvolutionRecommendation specifications.
    """

    ALL_STANDARD_DOMAINS = {"Agriculture", "Medicine", "Climate Science", "Biology", "Physics", "Chemistry"}

    def generate_recommendations(
        self,
        issues: List[EvolutionIssue],
        report: DatasetAnalysisReport,
    ) -> List[EvolutionRecommendation]:
        """
        Generate prioritized evolution recommendations based on identified dataset flaws.
        """
        logger.info(f"Generating evolution recommendations for {len(issues)} issue(s)...")

        recommendations: List[EvolutionRecommendation] = []
        rec_counter = 1

        existing_domains: Set[str] = set(report.general_statistics.domain_distribution.keys())
        missing_domains = list(self.ALL_STANDARD_DOMAINS - existing_domains)

        # 1. Check for Domain Diversity / Missing Domains
        if missing_domains:
            for domain in missing_domains[:3]:
                action = f"Generate missing scientific domain: {domain}"
                if domain == "Medicine":
                    action = "Generate clinical trials (Medicine)"
                elif domain in ("Physics", "Chemistry"):
                    action = f"Generate laboratory experiments ({domain})"
                elif domain in ("Climate Science", "Biology"):
                    action = f"Generate simulation studies ({domain})"

                rec = EvolutionRecommendation(
                    recommendation_id=f"rec-dom-{rec_counter:02d}",
                    category="DOMAIN_EXPANSION",
                    action_title=action,
                    reason=f"Domain '{domain}' is absent from current dataset distribution.",
                    priority=rec_counter,
                    severity=EvolutionSeverity.HIGH,
                    estimated_sample_count=20,
                    expected_health_improvement=8.5,
                    target_domain=domain,
                    target_difficulty="medium",
                )
                recommendations.append(rec)
                rec_counter += 1

        # 2. Check for Difficulty Imbalance (Hard samples < 30%)
        hard_count = report.general_statistics.difficulty_distribution.get("hard", 0)
        total_samples = report.general_statistics.total_samples
        hard_ratio = hard_count / max(1, total_samples)

        if hard_ratio < 0.30:
            rec = EvolutionRecommendation(
                recommendation_id=f"rec-diff-{rec_counter:02d}",
                category="DIFFICULTY_BALANCING",
                action_title="Generate harder reasoning samples",
                reason=f"Hard difficulty samples constitute only {hard_ratio * 100:.1f}% of dataset (Target >= 30%).",
                priority=rec_counter,
                severity=EvolutionSeverity.HIGH if hard_ratio < 0.15 else EvolutionSeverity.MEDIUM,
                estimated_sample_count=15,
                expected_health_improvement=6.0,
                target_domain=None,
                target_difficulty="hard",
            )
            recommendations.append(rec)
            rec_counter += 1

        # 3. Check for Low Experiment Diversity
        if report.diversity_metrics.experiment_diversity < 0.50:
            rec = EvolutionRecommendation(
                recommendation_id=f"rec-exp-{rec_counter:02d}",
                category="EXPERIMENT_DIVERSITY",
                action_title="Generate laboratory experiments & simulation studies",
                reason=f"Experiment diversity ratio is low ({report.diversity_metrics.experiment_diversity:.2f}). Require diverse experimental protocols.",
                priority=rec_counter,
                severity=EvolutionSeverity.HIGH,
                estimated_sample_count=15,
                expected_health_improvement=7.0,
                target_domain=None,
                target_difficulty=None,
            )
            recommendations.append(rec)
            rec_counter += 1

        # 4. Check for Low Failure Case Coverage or Diversity
        if report.reasoning_metrics.failure_case_coverage < 0.80 or report.diversity_metrics.failure_case_diversity < 0.50:
            rec = EvolutionRecommendation(
                recommendation_id=f"rec-fail-{rec_counter:02d}",
                category="FAILURE_CASE_EXPANSION",
                action_title="Increase failure case diversity",
                reason=f"Failure case coverage is {report.reasoning_metrics.failure_case_coverage * 100:.1f}%. Need edge case failure modes.",
                priority=rec_counter,
                severity=EvolutionSeverity.MEDIUM,
                estimated_sample_count=10,
                expected_health_improvement=5.0,
                target_domain=None,
                target_difficulty=None,
            )
            recommendations.append(rec)
            rec_counter += 1

        # 5. Check for Low Hypothesis Coverage or Diversity
        if report.reasoning_metrics.hypothesis_coverage < 0.90 or report.reasoning_metrics.alternative_hypothesis_coverage < 0.80:
            rec = EvolutionRecommendation(
                recommendation_id=f"rec-hyp-{rec_counter:02d}",
                category="HYPOTHESIS_DIVERSITY",
                action_title="Increase hypothesis diversity",
                reason=f"Primary or alternative hypothesis coverage is below benchmark threshold (Primary: {report.reasoning_metrics.hypothesis_coverage * 100:.1f}%).",
                priority=rec_counter,
                severity=EvolutionSeverity.HIGH,
                estimated_sample_count=10,
                expected_health_improvement=5.5,
                target_domain=None,
                target_difficulty=None,
            )
            recommendations.append(rec)
            rec_counter += 1

        # Re-sort recommendations strictly by priority
        recommendations.sort(key=lambda r: r.priority)
        return recommendations

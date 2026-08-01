"""
backend/app/benchmark/statistics.py — Benchmark Statistics Engine.

Computes metrics for Total Samples, Domain Distribution, Difficulty Distribution,
Knowledge Coverage, Reasoning Coverage, Experiment Diversity, Failure Diversity, and Adaptive Score.
"""

import logging
from typing import Dict, List

from app.benchmark.models import BenchmarkSample, BenchmarkStatistics

logger = logging.getLogger("dataset_genome.benchmark.statistics")


class BenchmarkStatisticsEngine:
    """
    Statistics computation engine assessing Dataset Genome Benchmark dataset composition and quality.
    """

    def compute_statistics(self, samples: List[BenchmarkSample]) -> BenchmarkStatistics:
        """
        Calculate full benchmark statistics metrics over dataset samples.
        """
        total = len(samples)
        logger.info(f"BenchmarkStatisticsEngine calculating statistics for {total} sample(s)...")

        domain_dist: Dict[str, int] = {}
        diff_dist: Dict[str, int] = {}

        total_fields_checked = 0
        populated_fields_count = 0
        failure_cases_count = 0
        experiment_protocol_types = set()

        for s in samples:
            domain_dist[s.domain] = domain_dist.get(s.domain, 0) + 1
            diff_dist[s.difficulty] = diff_dist.get(s.difficulty, 0) + 1

            # Check 16 fields for reasoning coverage
            fields = [
                s.sample_id, s.dataset_id, s.domain, s.difficulty, s.prompt,
                s.context, s.observation, s.problem_identification, s.research_gap,
                s.primary_hypothesis, s.alternative_hypothesis, s.expected_results,
                s.scientific_conclusion, s.experiment_design, s.evaluation_metrics,
                s.failure_cases
            ]
            total_fields_checked += len(fields)
            populated_fields_count += sum(1 for f in fields if f)

            if s.failure_cases:
                failure_cases_count += len(s.failure_cases)

            if s.experiment_design and "methodology" in s.experiment_design:
                experiment_protocol_types.add(str(s.experiment_design["methodology"])[:30])

        denom = max(1, total)

        # Knowledge coverage based on unique domain coverage and sample density
        domain_coverage = (len(domain_dist) / 10.0) * 100.0 if domain_dist else 0.0
        knowledge_coverage = round(min(100.0, domain_coverage * 0.8 + min(20.0, total * 0.5)), 1)

        # Reasoning coverage based on 16-field populating ratio
        reasoning_coverage = round((populated_fields_count / max(1, total_fields_checked)) * 100.0, 1)

        # Experiment diversity based on unique experiment methodology protocols
        exp_diversity = round(min(100.0, (len(experiment_protocol_types) / denom) * 100.0 + 30.0), 1)

        # Failure diversity based on negative control / failure cases presence
        fail_diversity = round(min(100.0, (failure_cases_count / denom) * 45.0 + 10.0), 1)

        # Composite Adaptive Score
        adaptive_score = round(
            knowledge_coverage * 0.25
            + reasoning_coverage * 0.35
            + exp_diversity * 0.20
            + fail_diversity * 0.20,
            1,
        )

        stats = BenchmarkStatistics(
            total_samples=total,
            domain_distribution=domain_dist,
            difficulty_distribution=diff_dist,
            knowledge_coverage=knowledge_coverage,
            reasoning_coverage=reasoning_coverage,
            experiment_diversity=exp_diversity,
            failure_diversity=fail_diversity,
            adaptive_score=adaptive_score,
        )

        logger.info(
            f"BenchmarkStatisticsEngine completed: Total={stats.total_samples}, "
            f"AdaptiveScore={stats.adaptive_score}/100, KnowledgeCoverage={stats.knowledge_coverage}%."
        )
        return stats

"""
backend/app/evaluation/leaderboard.py — Leaderboard Engine for Evaluation Framework.

MODULE 5 — Leaderboard.
Ranks datasets and models based on Adaptive Scores, Training Scores, Publication Scores,
and composite evaluation metrics.
"""

import logging
from typing import List, Optional

from app.evaluation.config import DEFAULT_EVALUATION_CONFIG, EvaluationConfig
from app.evaluation.models import BenchmarkRunRecord, LeaderboardEntry
from app.evaluation.metrics import MetricsEngine

logger = logging.getLogger("dataset_genome.evaluation.leaderboard")


class EvaluationLeaderboard:
    """
    MODULE 5 — Leaderboard.

    Maintains and constructs ranked dataset and model leaderboards based on empirical evaluation scores.
    """

    def __init__(self, config: EvaluationConfig = DEFAULT_EVALUATION_CONFIG) -> None:
        self.config = config
        self.metrics_engine = MetricsEngine(config=config)

    def generate_leaderboard(
        self,
        runs: List[BenchmarkRunRecord],
        domain_filter: Optional[str] = None,
    ) -> List[LeaderboardEntry]:
        """
        Rank dataset runs and return a sorted list of LeaderboardEntry items.
        """
        logger.info(f"EvaluationLeaderboard processing {len(runs)} benchmark run(s)...")

        filtered = runs
        if domain_filter:
            filtered = [r for r in runs if r.domain.lower() == domain_filter.lower()]

        entries: List[LeaderboardEntry] = []

        for run in filtered:
            ds = run.dataset_metrics
            m = run.model_metrics
            composite = self.metrics_engine.compute_composite_score(ds, m)

            # Publication score based on dataset health and training accuracy
            pub_score = round(min(100.0, ds.dataset_health * 0.5 + m.training_accuracy * 0.5), 1)

            entry = LeaderboardEntry(
                rank=1,  # Temporary rank
                dataset_version=run.dataset_version,
                dataset_type=run.dataset_type,
                domain=run.domain,
                model_version=run.model_version,
                adaptive_score=ds.adaptive_score,
                training_score=m.training_accuracy,
                publication_score=pub_score,
                composite_score=composite,
            )
            entries.append(entry)

        # Sort entries descending by composite score, then by training_score
        entries.sort(key=lambda x: (x.composite_score, x.training_score, x.adaptive_score), reverse=True)

        # Assign 1-indexed ranks
        for rank_idx, item in enumerate(entries, start=1):
            item.rank = rank_idx

        logger.info(f"EvaluationLeaderboard ranked {len(entries)} entries. Top dataset: '{entries[0].dataset_version if entries else 'None'}'.")
        return entries

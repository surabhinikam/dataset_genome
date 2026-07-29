"""
services/dataset_intelligence/health_score.py — Health Score Engine.

Combines individual profiler scores into a unified Dataset Health Score and grade.
"""

from typing import Dict
from schemas.intelligence import HealthScoreResult


class HealthScoreEngine:
    """
    Computes weighted overall health score and assigns grade tier.
    """

    # Weights sum up to 1.0 (100%)
    DEFAULT_WEIGHTS = {
        "completeness": 0.25,
        "consistency": 0.20,
        "feature_quality": 0.20,
        "noise": 0.15,
        "balance": 0.10,
        "correlation": 0.10,
    }

    def compute(self, profiler_scores: Dict[str, float]) -> HealthScoreResult:
        """
        Calculate overall health score from profiler score dictionary.
        """
        total_score = 0.0
        breakdown: Dict[str, float] = {}

        for key, weight in self.DEFAULT_WEIGHTS.items():
            score = float(profiler_scores.get(key, 100.0))
            score_clamped = max(0.0, min(100.0, score))
            breakdown[key] = round(score_clamped, 1)
            total_score += score_clamped * weight

        overall_score = round(total_score, 1)

        # Grade assignment & color token mapping
        if overall_score >= 85.0:
            grade = "Excellent"
            grade_color = "#10b981"  # Emerald
        elif overall_score >= 70.0:
            grade = "Good"
            grade_color = "#6366f1"  # Indigo
        elif overall_score >= 50.0:
            grade = "Fair"
            grade_color = "#f59e0b"  # Amber
        else:
            grade = "Poor"
            grade_color = "#ef4444"  # Red

        return HealthScoreResult(
            overall_score=overall_score,
            grade=grade,
            grade_color=grade_color,
            breakdown=breakdown,
        )

"""
services/autoscientist/comparison_engine.py — Metric Comparison Engine.

Compares baseline vs mutated quality metrics and computes signed MetricDelta objects.
"""

from typing import Dict, List
from services.autoscientist.evaluation_models import MetricDelta


class ComparisonEngine:
    """
    Computes pairwise metric comparisons between baseline and mutated datasets.
    """

    @classmethod
    def compare_metrics(
        cls,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float]
    ) -> List[MetricDelta]:
        """
        Compare before & after metric maps and generate MetricDelta list.
        """
        deltas: List[MetricDelta] = []
        lower_is_better_metrics = {"missing_rate", "duplicate_ratio", "outlier_ratio"}

        for metric_name, val_before in metrics_before.items():
            val_after = metrics_after.get(metric_name, val_before)
            abs_delta = round(val_after - val_before, 4)

            if val_before != 0:
                rel_pct = round((abs_delta / abs(val_before)) * 100.0, 2)
            else:
                rel_pct = 0.0 if abs_delta == 0 else 100.0

            if metric_name in lower_is_better_metrics:
                improved = val_after < val_before
            else:
                improved = val_after > val_before

            deltas.append(
                MetricDelta(
                    metric_name=metric_name,
                    value_before=val_before,
                    value_after=val_after,
                    absolute_delta=abs_delta,
                    relative_delta_pct=rel_pct,
                    improved=improved,
                )
            )

        return deltas

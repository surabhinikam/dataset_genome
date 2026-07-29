"""
services/autoscientist/metric_collector.py — Metric Collection Module.

Extracts normalized quality metrics from GenomeReportResponse objects.
"""

from typing import Dict
from schemas.intelligence import GenomeReportResponse


class MetricCollector:
    """
    Extracts standardized quality metrics from a GenomeReportResponse object.
    """

    @classmethod
    def collect_metrics(cls, report: GenomeReportResponse) -> Dict[str, float]:
        """
        Extract metrics map from GenomeReportResponse.
        """
        hs = report.health_score
        c = report.completeness
        curr = report.correlation
        b = report.balance
        n = report.noise
        cons = report.consistency
        fq = report.feature_quality

        breakdown = hs.breakdown if (hs and hasattr(hs, "breakdown") and hs.breakdown) else {}

        metrics: Dict[str, float] = {
            "health_score": float(hs.overall_score) if hs else 100.0,
            "quality_score": round(float(hs.overall_score) / 100.0, 4) if hs else 1.0,
            "completeness_score": float(breakdown.get("completeness", c.score if c else 100.0)),
            "correlation_score": float(breakdown.get("correlation", curr.score if curr else 100.0)),
            "balance_score": float(breakdown.get("balance", b.score if b else 100.0)),
            "noise_score": float(breakdown.get("noise", n.score if n else 100.0)),
            "consistency_score": float(breakdown.get("consistency", cons.score if cons else 100.0)),
            "feature_quality_score": float(breakdown.get("feature_quality", fq.score if fq else 100.0)),
            "missing_rate": float(c.missing_cell_ratio) if c else 0.0,
            "duplicate_ratio": float(cons.duplicate_ratio) if cons else 0.0,
            "outlier_ratio": float(n.outlier_ratio) if n else 0.0,
        }

        return metrics

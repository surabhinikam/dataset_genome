"""
services/dataset_intelligence/noise.py — Noise & Outlier Profiler using IQR Method.

Detects statistical outliers in numeric features via Interquartile Range (IQR).
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from schemas.intelligence import NoiseMetrics, ColumnOutlierDetail, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class NoiseProfiler(BaseProfiler):
    """
    Analyzes numerical dataset noise and outliers using the IQR (Interquartile Range) method.
    """

    @property
    def name(self) -> str:
        return "Noise & Outliers"

    def analyze(self, df: pd.DataFrame) -> Tuple[NoiseMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not num_cols or len(df) == 0:
            return (
                NoiseMetrics(
                    score=100.0,
                    total_outliers=0,
                    outlier_ratio=0.0,
                    column_outliers={},
                ),
                issues,
            )

        column_outliers: dict[str, ColumnOutlierDetail] = {}
        total_outliers = 0
        total_numeric_values = len(df) * len(num_cols)

        for col in num_cols:
            series = df[col].dropna()
            if len(series) < 4:
                continue

            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_count = len(outliers)
            outlier_ratio = float(outlier_count / len(series))

            total_outliers += outlier_count

            detail = ColumnOutlierDetail(
                q1=round(q1, 4),
                q3=round(q3, 4),
                iqr=round(iqr, 4),
                lower_bound=round(lower_bound, 4),
                upper_bound=round(upper_bound, 4),
                outlier_count=outlier_count,
                outlier_ratio=round(outlier_ratio, 4),
            )
            column_outliers[str(col)] = detail

            # Issue triggers
            if outlier_ratio > 0.15:
                issues.append(
                    DatasetIssue(
                        id=f"noise-critical-outliers-{col}",
                        title=f"Severe outliers in column '{col}'",
                        description=f"Column '{col}' contains {outlier_count} outliers ({outlier_ratio * 100:.1f}%) outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}].",
                        severity=IssueSeverity.CRITICAL,
                        column_name=str(col),
                        recommendation=f"Apply Winsorization, capping, or robust scaling (e.g. RobustScaler) to feature '{col}'.",
                    )
                )
            elif outlier_ratio > 0.05:
                issues.append(
                    DatasetIssue(
                        id=f"noise-warning-outliers-{col}",
                        title=f"Outliers detected in '{col}'",
                        description=f"Column '{col}' has {outlier_count} outliers ({outlier_ratio * 100:.1f}%) detected via IQR.",
                        severity=IssueSeverity.WARNING,
                        column_name=str(col),
                        recommendation=f"Investigate extreme values in '{col}' or clip at 1st/99th percentiles.",
                    )
                )

        overall_outlier_ratio = float(total_outliers / total_numeric_values) if total_numeric_values > 0 else 0.0
        score = max(0.0, min(100.0, round((1.0 - overall_outlier_ratio * 3.0) * 100.0, 1)))

        metrics = NoiseMetrics(
            score=score,
            total_outliers=total_outliers,
            outlier_ratio=round(overall_outlier_ratio, 4),
            column_outliers=column_outliers,
        )

        return metrics, issues

"""
services/dataset_intelligence/feature_quality.py — Feature Quality Profiler.

Identifies constant features (zero variance), low variance, and unusable ID-like columns.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from schemas.intelligence import FeatureQualityMetrics, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class FeatureQualityProfiler(BaseProfiler):
    """
    Analyzes feature quality, zero-variance columns, and identifier columns.
    """

    @property
    def name(self) -> str:
        return "Feature Quality"

    def analyze(self, df: pd.DataFrame) -> Tuple[FeatureQualityMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        total_features = len(df.columns)
        total_rows = len(df)

        if total_features == 0 or total_rows == 0:
            return (
                FeatureQualityMetrics(
                    score=100.0,
                    total_features=0,
                    constant_columns=[],
                    low_variance_columns=[],
                    id_like_columns=[],
                ),
                issues,
            )

        constant_columns: List[str] = []
        low_variance_columns: List[str] = []
        id_like_columns: List[str] = []

        for col in df.columns:
            series = df[col].dropna()
            if len(series) == 0:
                continue

            num_unique = series.nunique()

            # 1. Constant Column (zero variance)
            if num_unique <= 1:
                constant_columns.append(str(col))
                issues.append(
                    DatasetIssue(
                        id=f"feature-quality-constant-{col}",
                        title=f"Zero-variance constant feature '{col}'",
                        description=f"Column '{col}' contains only a single unique value across all rows.",
                        severity=IssueSeverity.CRITICAL,
                        column_name=str(col),
                        recommendation=f"Drop column '{col}' as it carries zero information for predictive modeling.",
                    )
                )
                continue

            # 2. Numeric low variance check
            if pd.api.types.is_numeric_dtype(df[col]):
                var = float(series.var()) if len(series) > 1 else 0.0
                if var < 1e-4:
                    low_variance_columns.append(str(col))
                    issues.append(
                        DatasetIssue(
                            id=f"feature-quality-low-var-{col}",
                            title=f"Near-zero variance in feature '{col}'",
                            description=f"Column '{col}' has near-zero variance ({var:.6f}).",
                            severity=IssueSeverity.WARNING,
                            column_name=str(col),
                            recommendation=f"Evaluate whether '{col}' provides useful signal or drop it.",
                        )
                    )

            # 3. ID-like column check (100% unique string/object column)
            if (df[col].dtype == "object" or df[col].dtype.name == "string") and total_rows > 10:
                if num_unique == total_rows:
                    id_like_columns.append(str(col))
                    issues.append(
                        DatasetIssue(
                            id=f"feature-quality-id-column-{col}",
                            title=f"ID-like feature detected in '{col}'",
                            description=f"Column '{col}' contains 100% unique text values ({num_unique}/{total_rows}), matching an ID pattern.",
                            severity=IssueSeverity.WARNING,
                            column_name=str(col),
                            recommendation=f"Exclude ID column '{col}' from predictive feature sets to prevent target leakage.",
                        )
                    )

        # Score calculation
        flawed_features_count = len(constant_columns) + len(id_like_columns)
        quality_ratio = float((total_features - flawed_features_count) / total_features)
        score = max(0.0, min(100.0, round(quality_ratio * 100.0, 1)))

        metrics = FeatureQualityMetrics(
            score=score,
            total_features=total_features,
            constant_columns=constant_columns,
            low_variance_columns=low_variance_columns,
            id_like_columns=id_like_columns,
        )

        return metrics, issues

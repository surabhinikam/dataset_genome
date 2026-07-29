"""
services/dataset_intelligence/consistency.py — Consistency Profiler.

Evaluates row uniqueness, duplicate rates, and data type uniformity across columns.
"""

from typing import Tuple, List
import pandas as pd
from schemas.intelligence import ConsistencyMetrics, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class ConsistencyProfiler(BaseProfiler):
    """
    Analyzes dataset consistency including duplicate rows and column type integrity.
    """

    @property
    def name(self) -> str:
        return "Consistency"

    def analyze(self, df: pd.DataFrame) -> Tuple[ConsistencyMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        total_rows = len(df)
        if total_rows == 0:
            return (
                ConsistencyMetrics(
                    score=100.0,
                    total_rows=0,
                    duplicate_rows=0,
                    duplicate_ratio=0.0,
                    type_uniformity_scores={},
                    mixed_type_columns=[],
                ),
                issues,
            )

        # 1. Duplicate row analysis
        duplicate_rows = int(df.duplicated().sum())
        duplicate_ratio = float(duplicate_rows / total_rows)

        if duplicate_ratio > 0.10:
            issues.append(
                DatasetIssue(
                    id="consistency-critical-duplicates",
                    title="Severe duplicate rows detected",
                    description=f"{duplicate_rows} duplicate rows ({duplicate_ratio * 100:.1f}% of total) found in dataset.",
                    severity=IssueSeverity.CRITICAL,
                    recommendation="Deduplicate dataset rows using df.drop_duplicates() before feature engineering.",
                )
            )
        elif duplicate_ratio > 0.01:
            issues.append(
                DatasetIssue(
                    id="consistency-warning-duplicates",
                    title="Duplicate rows present",
                    description=f"{duplicate_rows} duplicate rows ({duplicate_ratio * 100:.1f}% of total) found.",
                    severity=IssueSeverity.WARNING,
                    recommendation="Review and remove exact duplicate records.",
                )
            )

        # 2. Type uniformity analysis per column
        type_uniformity: dict[str, float] = {}
        mixed_type_columns: List[str] = []

        for col in df.columns:
            non_null_series = df[col].dropna()
            if len(non_null_series) == 0:
                type_uniformity[str(col)] = 1.0
                continue

            # Check types of Python values in the series
            types = non_null_series.map(lambda val: type(val).__name__).value_counts()
            majority_type_count = types.iloc[0] if len(types) > 0 else 0
            uniformity_score = float(majority_type_count / len(non_null_series))
            type_uniformity[str(col)] = round(uniformity_score, 4)

            if len(types) > 1 and uniformity_score < 0.95:
                mixed_type_columns.append(str(col))
                issues.append(
                    DatasetIssue(
                        id=f"consistency-mixed-types-{col}",
                        title=f"Mixed data types in column '{col}'",
                        description=f"Column '{col}' contains multiple data types ({dict(types)}).",
                        severity=IssueSeverity.WARNING,
                        column_name=str(col),
                        recommendation=f"Cast column '{col}' to a consistent data type (e.g. numeric or string).",
                    )
                )

        # Score calculation
        penalty = (duplicate_ratio * 50.0) + (len(mixed_type_columns) / max(1, len(df.columns)) * 50.0)
        score = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        metrics = ConsistencyMetrics(
            score=score,
            total_rows=total_rows,
            duplicate_rows=duplicate_rows,
            duplicate_ratio=round(duplicate_ratio, 4),
            type_uniformity_scores=type_uniformity,
            mixed_type_columns=mixed_type_columns,
        )

        return metrics, issues

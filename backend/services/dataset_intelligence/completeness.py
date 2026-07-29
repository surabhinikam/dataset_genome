"""
services/dataset_intelligence/completeness.py — Completeness Profiler.

Evaluates missing value proportions across cells, rows, and individual columns.
"""

from typing import Tuple, List
import pandas as pd
from schemas.intelligence import CompletenessMetrics, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class CompletenessProfiler(BaseProfiler):
    """
    Analyzes missing data completeness.
    """

    @property
    def name(self) -> str:
        return "Completeness"

    def analyze(self, df: pd.DataFrame) -> Tuple[CompletenessMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        total_rows, total_cols = df.shape
        total_cells = total_rows * total_cols

        if total_cells == 0:
            metrics = CompletenessMetrics(
                score=100.0,
                total_cells=0,
                missing_cells=0,
                missing_cell_ratio=0.0,
                complete_row_ratio=1.0,
                column_missing_rates={},
            )
            return metrics, issues

        # Count missing cells per column
        missing_per_col = df.isnull().sum()
        total_missing = int(missing_per_col.sum())
        missing_cell_ratio = float(total_missing / total_cells)

        # Complete rows (rows with 0 missing values)
        complete_rows = int(df.dropna().shape[0])
        complete_row_ratio = float(complete_rows / total_rows) if total_rows > 0 else 1.0

        # Per column missing rates
        column_missing_rates: dict[str, float] = {}
        for col in df.columns:
            missing_count = int(missing_per_col[col])
            rate = float(missing_count / total_rows) if total_rows > 0 else 0.0
            column_missing_rates[str(col)] = round(rate, 4)

            # Issue triggers
            if rate > 0.40:
                issues.append(
                    DatasetIssue(
                        id=f"completeness-critical-{col}",
                        title=f"Severe missing data in '{col}'",
                        description=f"Column '{col}' is missing {rate * 100:.1f}% of its values ({missing_count}/{total_rows} rows).",
                        severity=IssueSeverity.CRITICAL,
                        column_name=str(col),
                        recommendation=f"Consider dropping column '{col}' or collecting missing data before model training.",
                    )
                )
            elif rate > 0.10:
                issues.append(
                    DatasetIssue(
                        id=f"completeness-warning-{col}",
                        title=f"Moderate missing values in '{col}'",
                        description=f"Column '{col}' has {rate * 100:.1f}% missing values ({missing_count} rows).",
                        severity=IssueSeverity.WARNING,
                        column_name=str(col),
                        recommendation=f"Impute missing values in '{col}' using median/mode or model-based imputation.",
                    )
                )

        if missing_cell_ratio > 0.15:
            issues.append(
                DatasetIssue(
                    id="completeness-dataset-high-missing",
                    title="High overall dataset incompleteness",
                    description=f"{missing_cell_ratio * 100:.1f}% of all cells in the dataset are missing.",
                    severity=IssueSeverity.WARNING,
                    recommendation="Apply a comprehensive data imputation pipeline across all affected features.",
                )
            )

        # Score calculation: 100 - (missing_cell_ratio * 100)
        score = max(0.0, min(100.0, round((1.0 - missing_cell_ratio) * 100.0, 1)))

        metrics = CompletenessMetrics(
            score=score,
            total_cells=total_cells,
            missing_cells=total_missing,
            missing_cell_ratio=round(missing_cell_ratio, 4),
            complete_row_ratio=round(complete_row_ratio, 4),
            column_missing_rates=column_missing_rates,
        )

        return metrics, issues

"""
services/dataset_intelligence/correlation.py — Pearson Correlation Profiler.

Calculates pairwise Pearson correlation coefficients between numeric columns
and flags high multicollinearity (|r| > 0.85).
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from schemas.intelligence import CorrelationMetrics, CorrelationPair, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class CorrelationProfiler(BaseProfiler):
    """
    Analyzes pairwise linear correlations using Pearson's r.
    """

    @property
    def name(self) -> str:
        return "Correlation"

    def analyze(self, df: pd.DataFrame) -> Tuple[CorrelationMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        num_df = df.select_dtypes(include=[np.number])
        numeric_columns = [str(c) for c in num_df.columns]

        if len(numeric_columns) < 2 or len(df) == 0:
            return (
                CorrelationMetrics(
                    score=100.0,
                    numeric_columns=numeric_columns,
                    high_correlation_pairs=[],
                    matrix={},
                ),
                issues,
            )

        # Compute Pearson correlation matrix
        corr_matrix = num_df.corr(method="pearson").fillna(0.0)

        matrix_dict: dict[str, dict[str, float]] = {}
        high_corr_pairs: List[CorrelationPair] = []
        high_corr_count = 0

        for i, col1 in enumerate(numeric_columns):
            matrix_dict[col1] = {}
            for j, col2 in enumerate(numeric_columns):
                val = float(corr_matrix.iloc[i, j])
                val_rounded = round(val, 4)
                matrix_dict[col1][col2] = val_rounded

                # Upper triangle checks for multicollinearity (i < j)
                if i < j and abs(val) >= 0.85:
                    high_corr_count += 1
                    pair = CorrelationPair(
                        column_1=col1,
                        column_2=col2,
                        coefficient=val_rounded,
                    )
                    high_corr_pairs.append(pair)

                    issues.append(
                        DatasetIssue(
                            id=f"correlation-multicollinear-{col1}-{col2}",
                            title=f"High correlation between '{col1}' & '{col2}'",
                            description=f"Features '{col1}' and '{col2}' have a strong Pearson correlation coefficient of r = {val_rounded:.2f}.",
                            severity=IssueSeverity.WARNING,
                            column_name=f"{col1}, {col2}",
                            recommendation=f"Consider removing one of the correlated features ('{col1}' or '{col2}') or applying PCA.",
                        )
                    )

        # Penalty based on number of highly correlated pairs
        penalty = min(50.0, high_corr_count * 10.0)
        score = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        metrics = CorrelationMetrics(
            score=score,
            numeric_columns=numeric_columns,
            high_correlation_pairs=high_corr_pairs,
            matrix=matrix_dict,
        )

        return metrics, issues

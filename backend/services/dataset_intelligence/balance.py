"""
services/dataset_intelligence/balance.py — Balance Profiler.

Evaluates categorical class distribution, Shannon entropy, and class imbalance.
"""

import math
from typing import Tuple, List
import pandas as pd
from schemas.intelligence import BalanceMetrics, DatasetIssue, IssueSeverity
from services.dataset_intelligence.base import BaseProfiler


class BalanceProfiler(BaseProfiler):
    """
    Analyzes categorical class balance across dataset features.
    """

    @property
    def name(self) -> str:
        return "Balance"

    def analyze(self, df: pd.DataFrame) -> Tuple[BalanceMetrics, List[DatasetIssue]]:
        issues: List[DatasetIssue] = []

        categorical_entropy: dict[str, float] = {}
        majority_class_ratios: dict[str, float] = {}
        imbalanced_columns: List[str] = []

        # Filter categorical or object/string or low-cardinality discrete columns.
        # pandas >= 2.x on Python 3.13 uses StringDtype ("str") instead of "object"
        # for string columns, so dtype == "object" no longer matches.  Use the
        # dtype-agnostic pd.api.types.is_string_dtype() to cover both cases.
        cat_cols = [
            col for col in df.columns
            if pd.api.types.is_string_dtype(df[col])
            or df[col].dtype.name == "category"
            or (pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() <= 10)
        ]

        if not cat_cols:
            return (
                BalanceMetrics(
                    score=100.0,
                    categorical_entropy={},
                    majority_class_ratios={},
                    imbalanced_columns=[],
                ),
                issues,
            )

        total_imbalance_penalty = 0.0

        for col in cat_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue

            val_counts = series.value_counts()
            total_count = len(series)
            num_classes = len(val_counts)

            # Majority class ratio
            majority_ratio = float(val_counts.iloc[0] / total_count)
            majority_class_ratios[str(col)] = round(majority_ratio, 4)

            # Shannon Entropy calculation
            entropy = 0.0
            for count in val_counts:
                p = count / total_count
                if p > 0:
                    entropy -= p * math.log2(p)

            # Normalized entropy (0 to 1)
            max_entropy = math.log2(num_classes) if num_classes > 1 else 1.0
            norm_entropy = entropy / max_entropy if max_entropy > 0 else 1.0
            categorical_entropy[str(col)] = round(norm_entropy, 4)

            # Imbalance triggers
            if majority_ratio >= 0.85 and num_classes > 1:
                imbalanced_columns.append(str(col))
                total_imbalance_penalty += 30.0
                issues.append(
                    DatasetIssue(
                        id=f"balance-critical-imbalance-{col}",
                        title=f"Extreme class imbalance in '{col}'",
                        description=f"Dominant class '{val_counts.index[0]}' represents {majority_ratio * 100:.1f}% of column '{col}'.",
                        severity=IssueSeverity.CRITICAL,
                        column_name=str(col),
                        recommendation=f"Use resampling techniques (SMOTE/undersampling) or reframe feature '{col}'.",
                    )
                )
            elif majority_ratio > 0.80 and num_classes > 1:
                imbalanced_columns.append(str(col))
                total_imbalance_penalty += 15.0
                issues.append(
                    DatasetIssue(
                        id=f"balance-warning-imbalance-{col}",
                        title=f"Class imbalance detected in '{col}'",
                        description=f"Dominant class '{val_counts.index[0]}' occupies {majority_ratio * 100:.1f}% of column '{col}'.",
                        severity=IssueSeverity.WARNING,
                        column_name=str(col),
                        recommendation=f"Monitor model metrics (F1-score/PR-AUC) when evaluating with column '{col}'.",
                    )
                )

        score = max(0.0, min(100.0, round(100.0 - total_imbalance_penalty, 1)))

        metrics = BalanceMetrics(
            score=score,
            categorical_entropy=categorical_entropy,
            majority_class_ratios=majority_class_ratios,
            imbalanced_columns=imbalanced_columns,
        )

        return metrics, issues

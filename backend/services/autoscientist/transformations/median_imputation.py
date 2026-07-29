"""
services/autoscientist/transformations/median_imputation.py — Median/Mode Imputation Transformation.

Imputes missing numerical values with column median, and categorical values with column mode.
"""

from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from services.autoscientist.transformations.base import BaseTransformation


class MedianImputationTransformation(BaseTransformation):
    """Imputes missing values using median (numeric) or mode (categorical)."""

    @property
    def name(self) -> str:
        return "MedianImputationTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        transformed_df = df.copy()
        cols = target_columns or list(transformed_df.columns)

        imputed_cols: List[str] = []

        for col in cols:
            if col not in transformed_df.columns:
                continue
            if not transformed_df[col].isna().any():
                continue

            if pd.api.types.is_numeric_dtype(transformed_df[col]):
                median_val = transformed_df[col].median()
                transformed_df[col] = transformed_df[col].fillna(median_val)
                imputed_cols.append(f"{col} (median={median_val})")
            else:
                mode_series = transformed_df[col].mode()
                mode_val = mode_series.iloc[0] if not mode_series.empty else "missing"
                transformed_df[col] = transformed_df[col].fillna(mode_val)
                imputed_cols.append(f"{col} (mode='{mode_val}')")

        if imputed_cols:
            logs.append(f"Successfully applied Median/Mode imputation to column(s): {', '.join(imputed_cols)}")
        else:
            logs.append("No missing values required median imputation.")

        return transformed_df, logs, warnings

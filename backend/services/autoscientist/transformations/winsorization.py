"""
services/autoscientist/transformations/winsorization.py — Winsorization Transformation.

Clips numerical column values outside quantile percentile bounds (e.g. 1st - 99th percentiles).
"""

from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from services.autoscientist.transformations.base import BaseTransformation


class WinsorizationTransformation(BaseTransformation):
    """Clips numerical extreme values to upper and lower quantile bounds."""

    @property
    def name(self) -> str:
        return "WinsorizationTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        lower_q = float(parameters.get("lower_quantile", 0.01))
        upper_q = float(parameters.get("upper_quantile", 0.99))

        transformed_df = df.copy()
        cols = target_columns or list(transformed_df.select_dtypes(include=[np.number]).columns)

        clipped_cols: List[str] = []

        for col in cols:
            if col not in transformed_df.columns:
                continue
            if not pd.api.types.is_numeric_dtype(transformed_df[col]):
                warnings.append(f"Skipped non-numeric column '{col}' for Winsorization.")
                continue

            series = transformed_df[col].dropna()
            if len(series) < 5:
                continue

            lower_bound = float(series.quantile(lower_q))
            upper_bound = float(series.quantile(upper_q))

            transformed_df[col] = transformed_df[col].clip(lower=lower_bound, upper=upper_bound)
            clipped_cols.append(f"{col} [{lower_bound:.2f}, {upper_bound:.2f}]")

        if clipped_cols:
            logs.append(f"Applied Winsorization ({lower_q:.0%}-{upper_q:.0%} bounds) on column(s): {', '.join(clipped_cols)}")
        else:
            logs.append("No numeric columns clipped during Winsorization.")

        return transformed_df, logs, warnings

"""
services/autoscientist/transformations/feature_drop.py — Feature Drop & Pruning Transformations.

Removes zero-variance, redundant, or uninformative feature columns from a pandas DataFrame.
"""

from typing import Any, Dict, List, Tuple
import pandas as pd

from services.autoscientist.transformations.base import BaseTransformation


class FeatureDropTransformation(BaseTransformation):
    """Drops specified feature columns from a DataFrame."""

    @property
    def name(self) -> str:
        return "FeatureDropTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        drop_cols = parameters.get("drop_columns") or target_columns
        existing_drop_cols = [c for c in drop_cols if c in df.columns]

        if not existing_drop_cols:
            warnings.append(f"None of the target drop columns {drop_cols} exist in DataFrame.")
            return df.copy(), logs, warnings

        # Ensure at least 1 feature remains
        if len(existing_drop_cols) >= len(df.columns):
            raise ValueError(f"Cannot drop all columns {existing_drop_cols}; DataFrame must retain at least 1 feature.")

        transformed_df = df.drop(columns=existing_drop_cols)
        logs.append(f"Successfully dropped feature column(s): {existing_drop_cols}")
        return transformed_df, logs, warnings


class FeaturePruningTransformation(BaseTransformation):
    """Prunes a redundant feature column from a collinear feature pair."""

    @property
    def name(self) -> str:
        return "FeaturePruningTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        prune_col = parameters.get("prune_column") or (target_columns[0] if target_columns else None)
        retain_col = parameters.get("retain_column")

        if not prune_col or prune_col not in df.columns:
            warnings.append(f"Prune target column '{prune_col}' not found in DataFrame.")
            return df.copy(), logs, warnings

        transformed_df = df.drop(columns=[prune_col])
        logs.append(f"Pruned redundant collinear feature '{prune_col}' (retained feature '{retain_col}').")
        return transformed_df, logs, warnings

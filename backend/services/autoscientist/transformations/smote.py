"""
services/autoscientist/transformations/smote.py — SMOTE Class Rebalancing Transformation.

Rebalances imbalanced target classes via SMOTE or random oversampling fallback.
"""

from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from services.autoscientist.transformations.base import BaseTransformation


class SMOTEClassRebalancingTransformation(BaseTransformation):
    """Rebalances categorical target columns using SMOTE or random oversampling."""

    @property
    def name(self) -> str:
        return "ClassRebalancingTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        target_col = target_columns[0] if target_columns else None
        if not target_col or target_col not in df.columns:
            # Pick last column as fallback target
            target_col = df.columns[-1]

        transformed_df = df.copy()

        # Check if SMOTE from imblearn is available
        try:
            from imblearn.over_sampling import SMOTE
            has_smote = True
        except ImportError:
            has_smote = False

        val_counts = transformed_df[target_col].value_counts()
        if len(val_counts) <= 1:
            warnings.append(f"Target column '{target_col}' has only 1 class; cannot apply SMOTE.")
            return transformed_df, logs, warnings

        max_count = val_counts.max()

        if has_smote and pd.api.types.is_numeric_dtype(transformed_df[target_col]):
            try:
                numeric_df = transformed_df.select_dtypes(include=[np.number]).dropna()
                if not numeric_df.empty and target_col in numeric_df.columns:
                    X = numeric_df.drop(columns=[target_col])
                    y = numeric_df[target_col]
                    k_neigh = min(5, val_counts.min() - 1)
                    if k_neigh >= 1:
                        smote = SMOTE(sampling_strategy="auto", k_neighbors=k_neigh, random_state=42)
                        X_res, y_res = smote.fit_resample(X, y)
                        resampled_df = pd.DataFrame(X_res, columns=X.columns)
                        resampled_df[target_col] = y_res
                        logs.append(f"Applied SMOTE oversampling on target '{target_col}' (rows: {len(df)} -> {len(resampled_df)}).")
                        return resampled_df, logs, warnings
            except Exception as e:
                warnings.append(f"SMOTE execution failed ({str(e)}); falling back to random oversampling.")

        # Random oversampling fallback
        samples: List[pd.DataFrame] = []
        for cat_val, count in val_counts.items():
            cat_df = transformed_df[transformed_df[target_col] == cat_val]
            if count < max_count:
                resampled_cat = cat_df.sample(n=max_count, replace=True, random_state=42)
                samples.append(resampled_cat)
            else:
                samples.append(cat_df)

        resampled_df = pd.concat(samples, ignore_index=True)
        logs.append(f"Applied random oversampling on target '{target_col}' (rows: {len(df):,} -> {len(resampled_df):,}).")
        return resampled_df, logs, warnings

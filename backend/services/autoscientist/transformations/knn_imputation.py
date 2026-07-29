"""
services/autoscientist/transformations/knn_imputation.py — KNN Imputation Transformation.

Imputes missing numerical values using scikit-learn's KNNImputer (or median fallback if sklearn unavailable).
"""

from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from services.autoscientist.transformations.base import BaseTransformation


class KNNImputationTransformation(BaseTransformation):
    """Imputes missing numerical cell values using KNNImputer with median fallback."""

    @property
    def name(self) -> str:
        return "ImputationTransformation"

    def transform(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        logs: List[str] = []
        warnings: List[str] = []

        n_neighbors = parameters.get("n_neighbors", 5)
        weights = parameters.get("weights", "uniform")

        transformed_df = df.copy()
        numeric_cols = list(transformed_df.select_dtypes(include=[np.number]).columns)

        if not numeric_cols:
            warnings.append("No numeric columns found in DataFrame for KNN imputation.")
            return transformed_df, logs, warnings

        # Target numeric columns with missing values
        cols_to_impute = [c for c in numeric_cols if transformed_df[c].isna().any()]

        if not cols_to_impute:
            logs.append("No missing values found in numeric columns; skipping KNN imputation.")
            return transformed_df, logs, warnings

        try:
            from sklearn.impute import KNNImputer
            imputer = KNNImputer(n_neighbors=n_neighbors, weights=weights)
            imputed_array = imputer.fit_transform(transformed_df[numeric_cols])
            imputed_df = pd.DataFrame(imputed_array, columns=numeric_cols, index=transformed_df.index)
            for col in numeric_cols:
                transformed_df[col] = imputed_df[col]
            logs.append(f"Successfully applied KNNImputer(n_neighbors={n_neighbors}) to impute column(s): {cols_to_impute}")
        except ImportError:
            warnings.append("scikit-learn not installed; using median imputation fallback for KNN imputation.")
            for col in cols_to_impute:
                median_val = transformed_df[col].median()
                transformed_df[col] = transformed_df[col].fillna(median_val)
            logs.append(f"Applied median imputation fallback to column(s): {cols_to_impute}")

        return transformed_df, logs, warnings

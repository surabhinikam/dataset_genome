"""
services/autoscientist/hypothesis_constants.py — Constants & Parameter Factories for Scientific Hypothesis Generator.

Defines default evaluation metrics, risk levels, parameter factory defaults,
and metric delta bounds for scientific hypothesis synthesis.
"""

from enum import Enum
from typing import Any, Dict, List


class RiskLevel(str, Enum):
    """Risk classification for scientific dataset mutations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Metric Delta Bounding Constants
MIN_PREDICTED_METRIC_DELTA: float = 0.001
MAX_PREDICTED_METRIC_DELTA: float = 0.200
DEFAULT_EVALUATION_METRIC: str = "f1_score"


class ParameterFactory:
    """Reusable parameter factories for dataset mutation classes."""

    @staticmethod
    def feature_drop(drop_columns: List[str]) -> Dict[str, Any]:
        return {"drop_columns": drop_columns}

    @staticmethod
    def knn_imputation(n_neighbors: int = 5, weights: str = "uniform") -> Dict[str, Any]:
        return {"n_neighbors": n_neighbors, "weights": weights}

    @staticmethod
    def median_imputation(strategy: str = "median") -> Dict[str, Any]:
        return {"strategy": strategy}

    @staticmethod
    def mode_imputation(strategy: str = "most_frequent") -> Dict[str, Any]:
        return {"strategy": strategy}

    @staticmethod
    def winsorization(lower_quantile: float = 0.01, upper_quantile: float = 0.99) -> Dict[str, Any]:
        return {"lower_quantile": lower_quantile, "upper_quantile": upper_quantile}

    @staticmethod
    def smote(sampling_strategy: str = "auto", k_neighbors: int = 5) -> Dict[str, Any]:
        return {"sampling_strategy": sampling_strategy, "k_neighbors": k_neighbors}

    @staticmethod
    def feature_pruning(retain_column: str, prune_column: str) -> Dict[str, Any]:
        return {"retain_column": retain_column, "prune_column": prune_column}

    @staticmethod
    def row_deduplication(keep: str = "first") -> Dict[str, Any]:
        return {"keep": keep}

    @staticmethod
    def type_unification(target_type: str = "numeric_coerced") -> Dict[str, Any]:
        return {"target_type": target_type}

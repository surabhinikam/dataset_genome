"""
services/autoscientist/reasoning_constants.py — Constants for the Reasoning Engine.

Defines transformation class names, causal mechanisms, and default assumptions/risks
for deterministic template-based scientific reasoning.
"""

from enum import Enum
from typing import Dict, List, Tuple
from services.autoscientist.observation_constants import ObservationCategory


class TransformationClass(str, Enum):
    """Canonical dataset transformation classes recommended by the Reasoning Engine."""
    FEATURE_DROP = "FeatureDropTransformation"
    IMPUTATION = "ImputationTransformation"
    WINSORIZATION = "WinsorizationTransformation"
    FEATURE_PRUNING = "FeaturePruningTransformation"
    CLASS_REBALANCING = "ClassRebalancingTransformation"
    ROW_DEDUPLICATION = "RowDeduplicationTransformation"
    TYPE_UNIFICATION = "TypeUnificationTransformation"


# Default Causal Mechanisms per Category
DEFAULT_CAUSAL_MECHANISMS: Dict[ObservationCategory, str] = {
    ObservationCategory.FEATURE_QUALITY: (
        "Zero-variance structural non-informativeness or high-cardinality identifier leakage. "
        "The feature provides 0 predictive signal or induces target overfitting."
    ),
    ObservationCategory.COMPLETENESS: (
        "Missingness mechanism evaluated as Missing Completely at Random (MCAR) or Missing at Random (MAR). "
        "Missing cells introduce sample bias and degrade downstream estimator stability."
    ),
    ObservationCategory.CORRELATION: (
        "Linear feature redundancy and multicollinearity (|r| >= 0.85). "
        "Duplicate feature dimensions inflate model variance and distort feature importance weights."
    ),
    ObservationCategory.NOISE: (
        "Extreme statistical value corruption beyond interquartile bounds [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. "
        "Outliers distort mean/variance estimators and destabilize loss gradients."
    ),
    ObservationCategory.BALANCE: (
        "Categorical class distribution skewness leading to decision boundary collapse towards the majority class."
    ),
    ObservationCategory.CONSISTENCY: (
        "Exact row duplication or mixed data type parsing inconsistencies causing train-test data leakage."
    ),
}

# Standard Default Constraints
DEFAULT_SYSTEM_CONSTRAINTS: List[str] = [
    "Preserve original row order and indexing structure.",
    "Do not modify target feature column definitions.",
    "Ensure transformed output format remains CSV compliant."
]

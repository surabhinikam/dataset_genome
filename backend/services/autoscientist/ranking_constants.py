"""
services/autoscientist/ranking_constants.py — Constants & Weights for Problem Ranking Engine.

Defines multi-criteria utility weights, information loss risks, impact potentials,
and repair complexities for calibrating dataset flaw prioritization.
"""

from typing import Dict
from services.autoscientist.observation_constants import ObservationCategory

# Multi-Criteria Utility Weights (sum to 1.0)
WEIGHT_SEVERITY: float = 0.40
WEIGHT_INFO_LOSS_RISK: float = 0.30
WEIGHT_IMPACT_POTENTIAL: float = 0.20
WEIGHT_REPAIR_COMPLEXITY_PENALTY: float = 0.10

# Base Information Loss Risk Scores per Category (0.0 to 1.0)
CATEGORY_INFO_LOSS_RISK: Dict[ObservationCategory, float] = {
    ObservationCategory.FEATURE_QUALITY: 0.90,  # Zero-variance / ID features cause structural model bias
    ObservationCategory.COMPLETENESS: 0.85,     # Missing data reduces sample size & information content
    ObservationCategory.BALANCE: 0.65,          # Imbalance risks minority class decision boundary collapse
    ObservationCategory.NOISE: 0.50,            # Outliers distort gradient bounds & variance
    ObservationCategory.CORRELATION: 0.40,      # Multicollinearity inflates feature coefficient variance
    ObservationCategory.CONSISTENCY: 0.30,       # Duplicates & mixed types cause subtle data leakage
}

# Base Impact Potential Scores per Category (0.0 to 1.0)
CATEGORY_IMPACT_POTENTIAL: Dict[ObservationCategory, float] = {
    ObservationCategory.FEATURE_QUALITY: 0.95,  # Dropping constant features yields immediate clean gain
    ObservationCategory.COMPLETENESS: 0.85,     # Imputing/pruning missing data restores baseline integrity
    ObservationCategory.CORRELATION: 0.75,      # Removing redundant features reduces model complexity
    ObservationCategory.NOISE: 0.70,            # Clipping outliers improves tree split boundaries
    ObservationCategory.BALANCE: 0.65,          # Class rebalancing improves F1/AUC metrics
    ObservationCategory.CONSISTENCY: 0.50,       # Deduplication prevents test leakage
}

# Base Repair Complexity Scores (0.0 = trivial fix, 1.0 = highly complex fix)
CATEGORY_REPAIR_COMPLEXITY: Dict[ObservationCategory, float] = {
    ObservationCategory.FEATURE_QUALITY: 0.10,  # Trivial column drop
    ObservationCategory.CONSISTENCY: 0.20,       # Simple row deduplication or type casting
    ObservationCategory.CORRELATION: 0.30,      # Drop 1 of correlated pair
    ObservationCategory.NOISE: 0.40,            # Winsorization / quantile capping
    ObservationCategory.COMPLETENESS: 0.50,     # KNN / MICE Imputation
    ObservationCategory.BALANCE: 0.75,          # SMOTE / Adaptive Resampling
}

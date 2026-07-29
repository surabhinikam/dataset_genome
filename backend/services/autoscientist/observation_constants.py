"""
services/autoscientist/observation_constants.py — Constants & Thresholds for the Observation Engine.

Defines mathematical reference thresholds, category weights, confidence defaults,
and standard recommendation templates for statistical anomaly extraction.
"""

from enum import Enum
from typing import Dict


class ObservationCategory(str, Enum):
    """Supported categories for scientific data observations."""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    BALANCE = "balance"
    CORRELATION = "correlation"
    NOISE = "noise"
    FEATURE_QUALITY = "feature_quality"


# Category Weights for Severity Calculation
CATEGORY_SEVERITY_WEIGHTS: Dict[ObservationCategory, float] = {
    ObservationCategory.COMPLETENESS: 0.25,
    ObservationCategory.FEATURE_QUALITY: 0.20,
    ObservationCategory.NOISE: 0.20,
    ObservationCategory.CORRELATION: 0.15,
    ObservationCategory.BALANCE: 0.10,
    ObservationCategory.CONSISTENCY: 0.10,
}

# Mathematical Reference Thresholds
MISSING_CELL_RATIO_THRESHOLD: float = 0.05       # 5% missing cell ratio threshold
MISSING_COLUMN_RATIO_THRESHOLD: float = 0.10     # 10% column missing rate threshold
CRITICAL_COLUMN_MISSING_THRESHOLD: float = 0.50  # 50% severe missingness threshold

DUPLICATE_ROW_RATIO_THRESHOLD: float = 0.01      # 1% duplicate row ratio threshold
TYPE_UNIFORMITY_THRESHOLD: float = 0.95         # 95% type uniformity threshold

MAJORITY_CLASS_RATIO_THRESHOLD: float = 0.85     # 85% majority class imbalance threshold
SHANNON_ENTROPY_LOW_THRESHOLD: float = 0.40      # Low entropy threshold

PEARSON_CORRELATION_THRESHOLD: float = 0.85      # Severe correlation threshold |r| >= 0.85

OUTLIER_RATIO_THRESHOLD: float = 0.03            # 3% column outlier ratio threshold via IQR
SEVERE_OUTLIER_RATIO_THRESHOLD: float = 0.10     # 10% severe column outlier ratio

# Default Confidence Ratings
DEFAULT_CONFIDENCE: float = 0.95
HEURISTIC_CONFIDENCE: float = 0.85

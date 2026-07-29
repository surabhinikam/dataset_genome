"""
services/autoscientist/evaluation_constants.py — Evaluation Engine Constants.

Defines verification thresholds, calibration deltas, and outcome enums.
"""

from enum import Enum


class EvaluationOutcome(str, Enum):
    """Overall outcome of hypothesis verification."""
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    FAILED = "FAILED"


class EvaluationRecommendation(str, Enum):
    """Actionable recommendation produced by Evaluation Engine."""
    STORE_EXPERIMENT = "STORE_EXPERIMENT"
    RETRY_WITH_DIFFERENT_PARAMETERS = "RETRY_WITH_DIFFERENT_PARAMETERS"
    REJECT_HYPOTHESIS = "REJECT_HYPOTHESIS"
    INCREASE_CONFIDENCE = "INCREASE_CONFIDENCE"
    DECREASE_CONFIDENCE = "DECREASE_CONFIDENCE"


# Verification Thresholds
FULL_VERIFICATION_THRESHOLD = 0.70    # Actual improvement >= 70% of predicted -> VERIFIED
PARTIAL_VERIFICATION_THRESHOLD = 0.30 # Actual improvement >= 30% of predicted -> PARTIALLY_VERIFIED

# Confidence Calibration Adjustments
CONFIDENCE_CALIBRATION_BOOST = 0.05   # +0.05 confidence boost on VERIFIED
CONFIDENCE_CALIBRATION_PENALTY = -0.10 # -0.10 confidence penalty on FAILED

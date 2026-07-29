"""
services/autoscientist/hypothesis_verifier.py — Hypothesis Verification Module.

Compares predicted vs actual metric improvement, computes prediction error,
calibrates confidence, and produces actionable recommendations.
"""

from typing import Tuple
from services.autoscientist.evaluation_constants import (
    CONFIDENCE_CALIBRATION_BOOST,
    CONFIDENCE_CALIBRATION_PENALTY,
    FULL_VERIFICATION_THRESHOLD,
    PARTIAL_VERIFICATION_THRESHOLD,
    EvaluationOutcome,
    EvaluationRecommendation,
)


class HypothesisVerifier:
    """
    Verifies scientific hypotheses against actual observed mutation outcomes.
    """

    @classmethod
    def verify_hypothesis(
        cls,
        predicted_improvement: float,
        actual_improvement: float
    ) -> Tuple[EvaluationOutcome, float, EvaluationRecommendation, float]:
        """
        Verify hypothesis and compute outcome, error, recommendation, and confidence calibration.
        
        Returns:
            Tuple of (overall_result, prediction_error, recommendation, confidence_calibration)
        """
        prediction_error = round(abs(predicted_improvement - actual_improvement), 4)

        if predicted_improvement > 0:
            ratio = actual_improvement / predicted_improvement
        else:
            ratio = 1.0 if actual_improvement >= 0 else -1.0

        if ratio >= FULL_VERIFICATION_THRESHOLD or actual_improvement >= max(0.01, predicted_improvement):
            outcome = EvaluationOutcome.VERIFIED
            recommendation = EvaluationRecommendation.STORE_EXPERIMENT
            calibration = CONFIDENCE_CALIBRATION_BOOST

        elif ratio >= PARTIAL_VERIFICATION_THRESHOLD or actual_improvement > 0.0:
            outcome = EvaluationOutcome.PARTIALLY_VERIFIED
            recommendation = EvaluationRecommendation.RETRY_WITH_DIFFERENT_PARAMETERS
            calibration = 0.01

        else:
            outcome = EvaluationOutcome.FAILED
            recommendation = EvaluationRecommendation.REJECT_HYPOTHESIS
            calibration = CONFIDENCE_CALIBRATION_PENALTY

        return outcome, prediction_error, recommendation, calibration

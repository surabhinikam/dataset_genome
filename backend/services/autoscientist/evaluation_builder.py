"""
services/autoscientist/evaluation_builder.py — Fluent Builder Pattern for EvaluationReport.

Provides a fluid interface for constructing validated EvaluationReport domain objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport, MetricDelta
from services.autoscientist.evaluation_validator import EvaluationValidator


class EvaluationReportBuilder:
    """
    Fluent Builder for constructing EvaluationReport domain objects.
    """

    def __init__(self) -> None:
        self._evaluation_id: Optional[str] = None
        self._experiment_id: Optional[str] = None
        self._overall_result: EvaluationOutcome = EvaluationOutcome.VERIFIED
        self._hypothesis_verified: bool = True
        self._predicted_improvement: float = 0.05
        self._actual_improvement: float = 0.05
        self._prediction_error: float = 0.00
        self._metric_deltas: List[MetricDelta] = []
        self._health_score_before: float = 75.0
        self._health_score_after: float = 80.0
        self._quality_score_before: float = 0.75
        self._quality_score_after: float = 0.80
        self._recommendation: EvaluationRecommendation = EvaluationRecommendation.STORE_EXPERIMENT
        self._confidence_calibration: float = 0.05
        self._metadata: Dict[str, Any] = {}

    def with_evaluation_id(self, evaluation_id: str) -> "EvaluationReportBuilder":
        self._evaluation_id = evaluation_id
        return self

    def with_experiment_id(self, experiment_id: str) -> "EvaluationReportBuilder":
        self._experiment_id = experiment_id
        return self

    def with_overall_result(self, outcome: EvaluationOutcome) -> "EvaluationReportBuilder":
        self._overall_result = outcome
        self._hypothesis_verified = outcome in [EvaluationOutcome.VERIFIED, EvaluationOutcome.PARTIALLY_VERIFIED]
        return self

    def with_hypothesis_verified(self, verified: bool) -> "EvaluationReportBuilder":
        self._hypothesis_verified = verified
        return self

    def with_predicted_improvement(self, val: float) -> "EvaluationReportBuilder":
        self._predicted_improvement = val
        return self

    def with_actual_improvement(self, val: float) -> "EvaluationReportBuilder":
        self._actual_improvement = val
        return self

    def with_prediction_error(self, err: float) -> "EvaluationReportBuilder":
        self._prediction_error = max(0.0, err)
        return self

    def with_metric_deltas(self, deltas: List[MetricDelta]) -> "EvaluationReportBuilder":
        self._metric_deltas = deltas
        return self

    def with_health_scores(self, before: float, after: float) -> "EvaluationReportBuilder":
        self._health_score_before = before
        self._health_score_after = after
        self._quality_score_before = round(before / 100.0, 4)
        self._quality_score_after = round(after / 100.0, 4)
        return self

    def with_recommendation(self, rec: EvaluationRecommendation) -> "EvaluationReportBuilder":
        self._recommendation = rec
        return self

    def with_confidence_calibration(self, calibration: float) -> "EvaluationReportBuilder":
        self._confidence_calibration = calibration
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "EvaluationReportBuilder":
        self._metadata = metadata
        return self

    def build(self) -> EvaluationReport:
        """Validate required fields and return an EvaluationReport object."""
        if not self._evaluation_id:
            raise ValueError("EvaluationReport 'evaluation_id' is required")
        if not self._experiment_id:
            raise ValueError("EvaluationReport 'experiment_id' is required")

        report = EvaluationReport(
            evaluation_id=self._evaluation_id,
            experiment_id=self._experiment_id,
            overall_result=self._overall_result,
            hypothesis_verified=self._hypothesis_verified,
            predicted_improvement=self._predicted_improvement,
            actual_improvement=self._actual_improvement,
            prediction_error=self._prediction_error,
            metric_deltas=self._metric_deltas,
            health_score_before=self._health_score_before,
            health_score_after=self._health_score_after,
            quality_score_before=self._quality_score_before,
            quality_score_after=self._quality_score_after,
            recommendation=self._recommendation,
            confidence_calibration=self._confidence_calibration,
            metadata=self._metadata,
        )

        EvaluationValidator.validate_report(report)
        return report

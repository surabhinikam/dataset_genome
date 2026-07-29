"""
services/autoscientist/memory_builder.py — Fluent Builder for MemoryRecord Objects.

Implements the Builder pattern for constructing validated MemoryRecord domain objects.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.memory_models import MemoryRecord


class MemoryRecordBuilder:
    """
    Fluent Builder for constructing validated MemoryRecord instances.
    """

    def __init__(self) -> None:
        self._record_id: Optional[str] = None
        self._experiment_id: Optional[str] = None
        self._dataset_id: Optional[UUID] = None
        self._transformation_type: Optional[str] = None
        self._category: str = "completeness"
        self._health_score_before: Optional[float] = None
        self._health_score_after: Optional[float] = None
        self._predicted_improvement: Optional[float] = None
        self._actual_improvement: Optional[float] = None
        self._prediction_error: Optional[float] = None
        self._overall_result: Optional[EvaluationOutcome] = None
        self._hypothesis_verified: bool = False
        self._recommendation: Optional[EvaluationRecommendation] = None
        self._confidence_calibration: float = 0.0
        self._feature_vector: List[float] = []
        self._tags: List[str] = []
        self._metadata: Dict[str, Any] = {}
        self._stored_at: datetime = datetime.utcnow()

    def with_record_id(self, record_id: str) -> "MemoryRecordBuilder":
        self._record_id = record_id
        return self

    def with_experiment_id(self, experiment_id: str) -> "MemoryRecordBuilder":
        self._experiment_id = experiment_id
        return self

    def with_dataset_id(self, dataset_id: Optional[UUID]) -> "MemoryRecordBuilder":
        self._dataset_id = dataset_id
        return self

    def with_transformation_type(self, transformation_type: str) -> "MemoryRecordBuilder":
        self._transformation_type = transformation_type
        return self

    def with_category(self, category: str) -> "MemoryRecordBuilder":
        self._category = category
        return self

    def with_health_scores(self, health_before: float, health_after: float) -> "MemoryRecordBuilder":
        self._health_score_before = health_before
        self._health_score_after = health_after
        return self

    def with_improvements(self, predicted: float, actual: float, prediction_error: float) -> "MemoryRecordBuilder":
        self._predicted_improvement = predicted
        self._actual_improvement = actual
        self._prediction_error = prediction_error
        return self

    def with_overall_result(self, result: EvaluationOutcome) -> "MemoryRecordBuilder":
        self._overall_result = result
        return self

    def with_hypothesis_verified(self, verified: bool) -> "MemoryRecordBuilder":
        self._hypothesis_verified = verified
        return self

    def with_recommendation(self, recommendation: EvaluationRecommendation) -> "MemoryRecordBuilder":
        self._recommendation = recommendation
        return self

    def with_confidence_calibration(self, calibration: float) -> "MemoryRecordBuilder":
        self._confidence_calibration = calibration
        return self

    def with_feature_vector(self, vector: List[float]) -> "MemoryRecordBuilder":
        self._feature_vector = vector
        return self

    def with_tags(self, tags: List[str]) -> "MemoryRecordBuilder":
        self._tags = tags
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "MemoryRecordBuilder":
        self._metadata = metadata
        return self

    def build(self) -> MemoryRecord:
        """
        Validate mandatory fields and return a constructed MemoryRecord object.
        """
        if not self._record_id:
            self._record_id = f"mem-{uuid.uuid4().hex[:8]}"

        if not self._experiment_id:
            raise ValueError("MemoryRecord 'experiment_id' is required.")

        if not self._transformation_type:
            raise ValueError("MemoryRecord 'transformation_type' is required.")

        if self._health_score_before is None or self._health_score_after is None:
            raise ValueError("MemoryRecord baseline and mutated health scores are required.")

        if self._predicted_improvement is None or self._actual_improvement is None or self._prediction_error is None:
            raise ValueError("MemoryRecord improvements and prediction_error are required.")

        if not self._overall_result:
            self._overall_result = EvaluationOutcome.FAILED

        if not self._recommendation:
            self._recommendation = EvaluationRecommendation.RETRY_WITH_DIFFERENT_PARAMETERS

        return MemoryRecord(
            record_id=self._record_id,
            experiment_id=self._experiment_id,
            dataset_id=self._dataset_id,
            transformation_type=self._transformation_type,
            category=self._category,
            health_score_before=self._health_score_before,
            health_score_after=self._health_score_after,
            predicted_improvement=self._predicted_improvement,
            actual_improvement=self._actual_improvement,
            prediction_error=self._prediction_error,
            overall_result=self._overall_result,
            hypothesis_verified=self._hypothesis_verified,
            recommendation=self._recommendation,
            confidence_calibration=self._confidence_calibration,
            feature_vector=self._feature_vector,
            tags=self._tags,
            metadata=self._metadata,
            stored_at=self._stored_at,
        )

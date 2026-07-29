"""
services/autoscientist/memory_encoder.py — Experiment Feature Encoder for Scientific Memory.

Encodes EvaluationReport objects into normalized numerical feature vectors (8D)
and produces canonical MemoryRecord objects.
"""

from typing import List, Optional
from uuid import UUID

from services.autoscientist.evaluation_constants import EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.memory_builder import MemoryRecordBuilder
from services.autoscientist.memory_constants import FEATURE_VECTOR_DIMENSION
from services.autoscientist.memory_models import MemoryRecord


class MemoryEncoder:
    """
    Encoder for transforming EvaluationReport domain objects into normalized numerical feature vectors.
    """

    @classmethod
    def encode_feature_vector(cls, report: EvaluationReport) -> List[float]:
        """
        Encode an EvaluationReport into a normalized 8-dimensional numerical feature vector.
        
        Vector structure:
          [0]: health_score_before / 100.0
          [1]: health_score_after / 100.0
          [2]: predicted_improvement
          [3]: actual_improvement
          [4]: prediction_error
          [5]: confidence_calibration
          [6]: 1.0 if hypothesis_verified else 0.0
          [7]: recommendation_weight (1.0 for PROCEED, 0.5 for REVISE, 0.0 for ROLLBACK)
        """
        rec_weight = 0.5
        if report.recommendation == EvaluationRecommendation.STORE_EXPERIMENT:
            rec_weight = 1.0
        elif report.recommendation == EvaluationRecommendation.REJECT_HYPOTHESIS:
            rec_weight = 0.0

        vector = [
            round(report.health_score_before / 100.0, 4),
            round(report.health_score_after / 100.0, 4),
            round(float(report.predicted_improvement), 4),
            round(float(report.actual_improvement), 4),
            round(float(report.prediction_error), 4),
            round(float(report.confidence_calibration), 4),
            1.0 if report.hypothesis_verified else 0.0,
            rec_weight,
        ]

        assert len(vector) == FEATURE_VECTOR_DIMENSION
        return vector

    @classmethod
    def create_memory_record(
        cls,
        report: EvaluationReport,
        dataset_id: Optional[UUID] = None,
        transformation_type: Optional[str] = None,
        category: str = "completeness",
        tags: Optional[List[str]] = None,
    ) -> MemoryRecord:
        """
        Convert an EvaluationReport into a canonical MemoryRecord object.
        """
        feature_vector = cls.encode_feature_vector(report)
        meta = dict(report.metadata or {})

        trans_type = transformation_type or meta.get("transformation_type") or "UnknownTransformation"
        record_tags = tags or [trans_type.lower(), category.lower(), report.overall_result.value.lower()]

        builder = (
            MemoryRecordBuilder()
            .with_record_id(f"mem-{report.evaluation_id}")
            .with_experiment_id(report.experiment_id)
            .with_dataset_id(dataset_id)
            .with_transformation_type(trans_type)
            .with_category(category)
            .with_health_scores(report.health_score_before, report.health_score_after)
            .with_improvements(report.predicted_improvement, report.actual_improvement, report.prediction_error)
            .with_overall_result(report.overall_result)
            .with_hypothesis_verified(report.hypothesis_verified)
            .with_recommendation(report.recommendation)
            .with_confidence_calibration(report.confidence_calibration)
            .with_feature_vector(feature_vector)
            .with_tags(record_tags)
            .with_metadata(meta)
        )

        return builder.build()

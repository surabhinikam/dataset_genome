"""
services/autoscientist/memory_validator.py — Validation Engine for Scientific Memory.

Validates MemoryRecord fields, feature vector dimensions, and search parameters.
"""

from typing import List, Optional
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.memory_constants import FEATURE_VECTOR_DIMENSION
from services.autoscientist.memory_models import MemoryRecord, MemorySearchRequest


class MemoryValidator:
    """
    Validator for Scientific Memory Engine inputs and records.
    """

    @classmethod
    def validate_record(cls, record: MemoryRecord) -> None:
        """
        Validate a MemoryRecord instance.
        
        Raises ValueError if mandatory fields or dimensions are invalid.
        """
        if not record.record_id:
            raise ValueError("MemoryRecord record_id cannot be empty.")

        if not record.experiment_id:
            raise ValueError("MemoryRecord experiment_id cannot be empty.")

        if not record.transformation_type:
            raise ValueError("MemoryRecord transformation_type cannot be empty.")

        if record.feature_vector and len(record.feature_vector) != FEATURE_VECTOR_DIMENSION:
            raise ValueError(
                f"MemoryRecord feature_vector dimension mismatch. "
                f"Expected {FEATURE_VECTOR_DIMENSION}D, got {len(record.feature_vector)}D."
            )

    @classmethod
    def validate_evaluation_report(cls, report: EvaluationReport) -> None:
        """
        Validate an EvaluationReport prior to memory encoding and storage.
        """
        if not report.evaluation_id:
            raise ValueError("EvaluationReport evaluation_id cannot be empty.")

        if not report.experiment_id:
            raise ValueError("EvaluationReport experiment_id cannot be empty.")

    @classmethod
    def validate_search_request(cls, request: MemorySearchRequest) -> None:
        """
        Validate search query parameters.
        """
        if request.top_k < 1 or request.top_k > 100:
            raise ValueError(f"Invalid top_k search parameter '{request.top_k}'. Must be between 1 and 100.")

        if request.query_vector and len(request.query_vector) != FEATURE_VECTOR_DIMENSION:
            raise ValueError(
                f"Search query_vector dimension mismatch. "
                f"Expected {FEATURE_VECTOR_DIMENSION}D, got {len(request.query_vector)}D."
            )

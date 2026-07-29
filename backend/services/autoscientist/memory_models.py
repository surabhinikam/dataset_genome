"""
services/autoscientist/memory_models.py — Pydantic Models for Scientific Memory Engine.

Defines MemoryRecord, MemoryStore, MemoryRetrievalResult, and REST API DTOs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.memory_constants import FEATURE_VECTOR_DIMENSION, SimilarityMetric


class MemoryRecord(BaseModel):
    """
    Structured Memory Record representing a stored past experimental mutation and outcome.
    
    Serves as the canonical experience unit in the Scientific Memory Engine.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    record_id: str = Field(..., description="Unique slug identifier for the memory record")
    experiment_id: str = Field(..., description="ID of the underlying experiment / plan")
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    transformation_type: str = Field(..., description="Class name of the executed transformation")
    category: str = Field("completeness", description="Profiler observation category")
    health_score_before: float = Field(..., ge=0.0, le=100.0, description="Baseline health score")
    health_score_after: float = Field(..., ge=0.0, le=100.0, description="Mutated health score")
    predicted_improvement: float = Field(..., description="Predicted metric improvement delta")
    actual_improvement: float = Field(..., description="Actual observed metric improvement delta")
    prediction_error: float = Field(..., description="Absolute prediction error |predicted - actual|")
    overall_result: EvaluationOutcome = Field(..., description="Verification outcome: VERIFIED, PARTIALLY_VERIFIED, FAILED")
    hypothesis_verified: bool = Field(..., description="Whether hypothesis was verified")
    recommendation: EvaluationRecommendation = Field(..., description="Actionable recommendation verdict")
    confidence_calibration: float = Field(..., description="Calibrated confidence adjustment delta")
    feature_vector: List[float] = Field(
        default_factory=list,
        description=f"Normalized numerical feature vector ({FEATURE_VECTOR_DIMENSION}D)"
    )
    tags: List[str] = Field(default_factory=list, description="Categorical index tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    stored_at: datetime = Field(default_factory=datetime.utcnow, description="Storage timestamp")


class MemoryStore(BaseModel):
    """Container holding active MemoryRecords and global transformation statistics."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_records: int = Field(0, ge=0, description="Count of stored memory records")
    records: List[MemoryRecord] = Field(default_factory=list, description="List of stored MemoryRecord objects")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class MemoryRetrievalResult(BaseModel):
    """Result payload returned by similarity search in the Scientific Memory Engine."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    query_record_id: Optional[str] = Field(None, description="ID of query record if applicable")
    similar_records: List[MemoryRecord] = Field(default_factory=list, description="Ranked list of similar memory records")
    similarity_scores: List[float] = Field(default_factory=list, description="Corresponding similarity scores [0.0..1.0]")
    historical_success_rate: float = Field(0.50, ge=0.0, le=1.0, description="Historical success rate for category/transformation")
    recommended_transformation: Optional[str] = Field(None, description="Top recommended transformation class")
    blacklisted_transformations: List[str] = Field(default_factory=list, description="List of blacklisted transformation classes")
    confidence_calibration_adjustment: float = Field(0.0, description="Calibrated confidence adjustment delta")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow, description="Retrieval timestamp")


class MemoryStoreRequest(BaseModel):
    """Request DTO for POST /autoscientist/memory/store."""
    evaluation_report: Optional[EvaluationReport] = Field(None, description="EvaluationReport object to store")
    dataset_id: Optional[UUID] = Field(None, description="Optional dataset UUID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }
    }


class MemoryStoreResponse(BaseModel):
    """Response DTO for POST /autoscientist/memory/store."""
    record_id: str = Field(..., description="ID of stored memory record")
    experiment_id: str = Field(..., description="Underlying experiment ID")
    memory_record: MemoryRecord = Field(..., description="Stored MemoryRecord object")
    stored_at: datetime = Field(default_factory=datetime.utcnow, description="Storage timestamp")


class MemorySearchRequest(BaseModel):
    """Request DTO for POST /autoscientist/memory/search."""
    dataset_id: Optional[UUID] = Field(None, description="Optional dataset UUID")
    category: Optional[str] = Field(None, description="Profiler category filter (e.g. 'completeness')")
    transformation_type: Optional[str] = Field(None, description="Transformation class filter")
    metric: SimilarityMetric = Field(SimilarityMetric.COSINE, description="Distance metric to use")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of similar records to return")
    query_vector: Optional[List[float]] = Field(None, description="Explicit feature vector query")
    evaluation_report: Optional[EvaluationReport] = Field(None, description="Optional evaluation report to search against")

    model_config = {
        "json_schema_extra": {
            "example": {
                "category": "completeness",
                "transformation_type": "KNNImputationTransformation",
                "top_k": 5,
                "metric": "cosine"
            }
        }
    }


class MemorySearchResponse(BaseModel):
    """Response DTO for POST /autoscientist/memory/search."""
    total_matches: int = Field(..., ge=0, description="Count of matched similar records")
    retrieval_result: MemoryRetrievalResult = Field(..., description="Detailed retrieval result")
    searched_at: datetime = Field(default_factory=datetime.utcnow, description="Search timestamp")

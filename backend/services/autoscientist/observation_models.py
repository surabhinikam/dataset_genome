"""
services/autoscientist/observation_models.py — Pydantic Schemas for Scientific Observations.

Defines the ScientificObservation Pydantic v2 domain model and the REST API
request/response DTOs for the POST /autoscientist/observe endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_constants import ObservationCategory


class ScientificObservation(BaseModel):
    """
    Structured scientific observation extracted from a dataset Genome Report.
    
    Represents an empirical data flaw, abnormality, or statistical property
    that serves as the input to the AutoScientist reasoning and evolution loop.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(..., description="Unique slug for the observation")
    category: ObservationCategory = Field(..., description="Profiler category")
    title: str = Field(..., description="Short, descriptive observation title")
    summary: str = Field(..., description="Detailed statistical observation summary")
    affected_columns: List[str] = Field(default_factory=list, description="List of affected column names")
    severity: float = Field(..., ge=0.0, le=1.0, description="Normalized severity score between 0.0 and 1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence score between 0.0 and 1.0")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Structured empirical evidence payload")
    recommendations: List[str] = Field(default_factory=list, description="Actionable remediation steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")


class ObservationRequest(BaseModel):
    """Request payload for POST /autoscientist/observe."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of an uploaded dataset")
    report: Optional[GenomeReportResponse] = Field(None, description="Direct GenomeReportResponse payload")


class ObservationResponse(BaseModel):
    """Response payload for POST /autoscientist/observe."""
    dataset_id: UUID = Field(..., description="UUID of the analyzed dataset")
    filename: str = Field(..., description="Filename of the dataset")
    total_observations: int = Field(..., ge=0, description="Count of extracted scientific observations")
    overall_health_score: float = Field(..., ge=0.0, le=100.0, description="Overall dataset health score")
    observations: List[ScientificObservation] = Field(..., description="Extracted scientific observations")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

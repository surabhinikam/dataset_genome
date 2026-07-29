"""
services/autoscientist/ranking_models.py — Pydantic Schemas for Problem Ranking.

Defines RankedProblem, PrioritizedProblemQueue, UtilityComponents, and REST API DTOs.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_models import ScientificObservation


class UtilityComponents(BaseModel):
    """Normalized multi-criteria utility score breakdown for a scientific observation."""
    severity: float = Field(..., ge=0.0, le=1.0, description="Normalized anomaly severity")
    information_loss_risk: float = Field(..., ge=0.0, le=1.0, description="Risk of information loss if unaddressed")
    impact_potential: float = Field(..., ge=0.0, le=1.0, description="Expected performance gain from remediation")
    repair_complexity: float = Field(..., ge=0.0, le=1.0, description="Computational and engineering fix complexity")


class RankedProblem(BaseModel):
    """
    Scientific problem prioritized by the Problem Ranking Engine.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    rank: int = Field(..., ge=1, description="1-indexed priority ranking")
    observation_id: str = Field(..., description="ID of the underlying ScientificObservation")
    observation: ScientificObservation = Field(..., description="The full ScientificObservation object")
    utility_score: float = Field(..., ge=0.0, le=1.0, description="Final scalar utility score")
    component_scores: UtilityComponents = Field(..., description="Detailed component utility breakdown")
    explanation: str = Field(..., description="Human-readable justification for the utility score and ranking")
    recommended_next_step: str = Field(..., description="Actionable recommendation for the AutoScientist hypothesis generator")


class PrioritizedProblemQueue(BaseModel):
    """
    Deterministic queue of ranked dataset problems ready for scientific hypothesis generation.
    """
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    total_problems: int = Field(..., ge=0, description="Total count of prioritized problems")
    ranked_problems: List[RankedProblem] = Field(default_factory=list, description="Ordered list of ranked problems")
    highest_priority_problem: Optional[RankedProblem] = Field(None, description="The top #1 prioritized problem, if any")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Queue generation timestamp")


class RankRequest(BaseModel):
    """Request DTO for POST /autoscientist/rank."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of an uploaded dataset")
    observations: Optional[List[ScientificObservation]] = Field(None, description="List of ScientificObservation objects")
    report: Optional[GenomeReportResponse] = Field(None, description="Raw GenomeReportResponse JSON object")


class RankResponse(BaseModel):
    """Response DTO for POST /autoscientist/rank."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    total_problems: int = Field(..., ge=0, description="Total count of ranked problems")
    queue: PrioritizedProblemQueue = Field(..., description="Complete PrioritizedProblemQueue")
    ranked_problems: List[RankedProblem] = Field(..., description="List of ranked problems")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

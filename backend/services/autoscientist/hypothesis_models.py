"""
services/autoscientist/hypothesis_models.py — Pydantic Schemas for Scientific Hypotheses.

Defines ScientificHypothesis, RiskLevel, and REST API DTOs for POST /autoscientist/hypothesis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.hypothesis_constants import RiskLevel
from services.autoscientist.reasoning_models import ReasoningTrace


class ScientificHypothesis(BaseModel):
    """
    Testable, measurable, and falsifiable Scientific Hypothesis.
    
    Synthesized from a Causal ReasoningTrace, this claim specifies the proposed
    transformation, target column, exact parameters, target evaluation metric,
    and predicted metric delta for downstream execution by the Experiment Planner.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(..., description="Unique slug for the scientific hypothesis")
    problem_id: str = Field(..., description="ID of the underlying RankedProblem")
    statement: str = Field(..., description="Testable and falsifiable scientific hypothesis statement claim")
    observation_summary: str = Field(..., description="Summary of the empirical observation")
    causal_mechanism: str = Field(..., description="Inferred underlying causal flaw mechanism")
    transformation_type: str = Field(..., description="Recommended dataset transformation class name")
    target_column: Optional[str] = Field(None, description="Primary affected target column name, if applicable")
    proposed_parameters: Dict[str, Any] = Field(default_factory=dict, description="Structured mutation parameters")
    target_evaluation_metric: str = Field("f1_score", description="Evaluation metric targeted for improvement")
    predicted_metric_delta: float = Field(..., ge=0.001, le=0.200, description="Predicted positive metric gain [0.001, 0.200]")
    estimated_confidence: float = Field(..., ge=0.0, le=1.0, description="Estimated scientific confidence [0.0, 1.0]")
    risk_level: RiskLevel = Field(..., description="Assessed mutation risk level: low, medium, or high")
    dependencies: List[str] = Field(default_factory=list, description="Required software or system dependencies")
    expected_side_effects: List[str] = Field(default_factory=list, description="Anticipated dataset side-effects")
    assumptions: List[str] = Field(default_factory=list, description="Underlying scientific assumptions")
    constraints: List[str] = Field(default_factory=list, description="Operational data invariants")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class HypothesisRequest(BaseModel):
    """Request DTO for POST /autoscientist/hypothesis."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of an uploaded dataset")
    reasoning_trace: Optional[ReasoningTrace] = Field(None, description="Direct ReasoningTrace object payload")
    reasoning_id: Optional[str] = Field(None, description="ID of an existing reasoning trace")
    report: Optional[GenomeReportResponse] = Field(None, description="Raw GenomeReportResponse JSON object")


class HypothesisResponse(BaseModel):
    """Response DTO for POST /autoscientist/hypothesis."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    problem_id: str = Field(..., description="ID of the underlying RankedProblem")
    hypothesis: ScientificHypothesis = Field(..., description="Synthesized ScientificHypothesis object")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

"""
services/autoscientist/research_models.py — Pydantic Models for Scientific Research Notebook.

Defines NotebookStage, NotebookEntry, TimelineEvent, ResearchNotebook, and REST API DTOs.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.execution_models import ExecutionResult
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.memory_models import MemoryRecord
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_models import ReasoningTrace


class NotebookStage(str, Enum):
    """Supported 8 stages of the AutoScientist scientific workflow."""
    OBSERVATION = "OBSERVATION"
    RANKING = "RANKING"
    REASONING = "REASONING"
    HYPOTHESIS = "HYPOTHESIS"
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    EVALUATION = "EVALUATION"
    LESSONS_LEARNED = "LESSONS_LEARNED"


class NotebookEntry(BaseModel):
    """
    Individual notebook entry representing a single stage in the scientific workflow.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    entry_id: str = Field(..., description="Unique slug identifier for the notebook entry")
    stage: NotebookStage = Field(..., description="Workflow stage enum")
    stage_title: str = Field(..., description="Human-readable title of the stage")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Stage execution timestamp")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Inputs provided to the stage")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs produced by the stage")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Stage confidence score [0.0..1.0]")
    reasoning: str = Field("", description="Natural language reasoning summary")
    artifacts: List[str] = Field(default_factory=list, description="List of generated artifact paths or references")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Key-value quantitative metrics")
    dataset_version: str = Field("v1.0.0", description="Dataset version tag at this stage")
    experiment_version: str = Field("v1.0.0", description="Experiment version tag")
    status: str = Field("COMPLETED", description="Stage status: COMPLETED, FAILED, PENDING")
    ui_color: str = Field("#3B82F6", description="HEX/Tailwind color token for frontend rendering")


class TimelineEvent(BaseModel):
    """
    Frontend-ready event model designed for rendering interactive UI timelines directly.
    """
    event_id: str = Field(..., description="Unique event identifier")
    stage_name: str = Field(..., description="Name of the scientific stage")
    label: str = Field(..., description="Short display label")
    summary: str = Field(..., description="Short summary for timeline item")
    timestamp: datetime = Field(..., description="Event timestamp")
    status: str = Field(..., description="Status badge string")
    color: str = Field(..., description="HEX color token for timeline node")
    icon: str = Field("microscope", description="Icon identifier for frontend UI")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed attributes payload")


class ResearchNotebook(BaseModel):
    """
    Complete composite Scientific Research Notebook recording an entire experiment lineage.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    notebook_id: str = Field(..., description="Unique slug for the research notebook")
    experiment_id: str = Field(..., description="ID of the underlying experiment / plan")
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    title: str = Field(..., description="Notebook title")
    summary: str = Field(..., description="Executive summary of the experiment")
    overall_outcome: str = Field("VERIFIED", description="Overall verification outcome")
    entries: List[NotebookEntry] = Field(default_factory=list, description="Ordered 8-stage notebook entries")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Frontend-ready timeline events")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Notebook creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class NotebookCreateRequest(BaseModel):
    """Request DTO for POST /autoscientist/notebook."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of the dataset")
    experiment_id: Optional[str] = Field(None, description="Optional experiment ID")
    report: Optional[GenomeReportResponse] = Field(None, description="Baseline report")
    observation: Optional[ScientificObservation] = Field(None, description="Observation object")
    ranked_problem: Optional[RankedProblem] = Field(None, description="Ranked problem object")
    reasoning_trace: Optional[ReasoningTrace] = Field(None, description="Reasoning trace object")
    hypothesis: Optional[ScientificHypothesis] = Field(None, description="Hypothesis object")
    plan: Optional[ExperimentPlan] = Field(None, description="Experiment plan object")
    execution_result: Optional[ExecutionResult] = Field(None, description="Execution result object")
    evaluation_report: Optional[EvaluationReport] = Field(None, description="Evaluation report object")
    memory_record: Optional[MemoryRecord] = Field(None, description="Memory record object")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "experiment_id": "exp-sample-123"
            }
        }
    }


class NotebookResponse(BaseModel):
    """Response DTO for POST /autoscientist/notebook."""
    notebook_id: str = Field(..., description="ID of the research notebook")
    experiment_id: str = Field(..., description="Underlying experiment ID")
    notebook: ResearchNotebook = Field(..., description="Complete ResearchNotebook object")
    markdown_report: str = Field(..., description="Rendered GitHub-Flavored Markdown report")
    json_report: Dict[str, Any] = Field(..., description="Structured JSON report dictionary")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

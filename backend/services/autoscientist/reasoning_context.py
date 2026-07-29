"""
services/autoscientist/reasoning_context.py — Reasoning Context Container.

Encapsulates dataset metadata, genome report, observations, prioritized problem,
health score, operational objectives, constraints, and Scientific Memory interface.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_models import ScientificMemoryInterface


class ReasoningContext(BaseModel):
    """
    Complete context container provided as input to the Reasoning Engine.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    filename: Optional[str] = Field("dataset.csv", description="Dataset filename")
    genome_report: Optional[GenomeReportResponse] = Field(None, description="Raw GenomeReportResponse object")
    observations: List[ScientificObservation] = Field(default_factory=list, description="All extracted scientific observations")
    prioritized_problem: RankedProblem = Field(..., description="The target RankedProblem to reason about")
    health_score: float = Field(100.0, ge=0.0, le=100.0, description="Overall dataset health score")
    objectives: List[str] = Field(
        default_factory=lambda: [
            "Maximize downstream model predictive performance (F1 / Accuracy / ROC-AUC).",
            "Maintain dataset statistical integrity and prevent train-test data leakage.",
            "Minimize unnecessary feature loss and unnecessary row deletion."
        ],
        description="Scientific optimization objectives"
    )
    constraints: List[str] = Field(
        default_factory=lambda: [
            "Do not modify target variable column definitions.",
            "Preserve original row count where feasible.",
            "Maintain valid tabular pandas DataFrame schema."
        ],
        description="Engineering and data invariants"
    )
    memory_interface: ScientificMemoryInterface = Field(
        default_factory=ScientificMemoryInterface,
        description="Interface stub for future Scientific Memory Engine integration"
    )

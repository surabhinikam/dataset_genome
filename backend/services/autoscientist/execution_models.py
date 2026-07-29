"""
services/autoscientist/execution_models.py — Pydantic Schemas for Dataset Execution Engine.

Defines ExecutionResult, ExecutionStatus, and REST API DTOs for POST /autoscientist/execute.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.hypothesis_models import ScientificHypothesis


class ExecutionStatus(str, Enum):
    """Execution status for dataset experiment transformations."""
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ExecutionResult(BaseModel):
    """
    Result of executing an ExperimentPlan on a dataset.
    
    Contains transformed dataset lineage version tags, storage paths, runtime
    metrics, row/column counts before and after mutation, logs, warnings, and errors.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    execution_id: str = Field(..., description="Unique slug for the execution run")
    plan_id: str = Field(..., description="ID of the underlying ExperimentPlan")
    status: ExecutionStatus = Field(..., description="Execution status: completed, failed, or rejected")
    dataset_version: str = Field(..., description="Output lineage dataset version tag (e.g. v1.1.0)")
    output_dataset_path: str = Field(..., description="Absolute file storage path for transformed CSV")
    execution_time_ms: float = Field(..., ge=0.0, description="Execution duration in milliseconds")
    memory_usage_mb: float = Field(..., ge=0.0, description="Peak memory usage in Megabytes")
    rows_before: int = Field(..., ge=0, description="Dataset row count prior to mutation")
    rows_after: int = Field(..., ge=0, description="Dataset row count post mutation")
    columns_before: int = Field(..., ge=0, description="Dataset column count prior to mutation")
    columns_after: int = Field(..., ge=0, description="Dataset column count post mutation")
    logs: List[str] = Field(default_factory=list, description="Execution log messages")
    warnings: List[str] = Field(default_factory=list, description="Execution warning messages")
    errors: List[str] = Field(default_factory=list, description="Execution error messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    executed_at: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")


class ExecuteRequest(BaseModel):
    """Request DTO for POST /autoscientist/execute."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of an uploaded dataset")
    experiment_plan: Optional[ExperimentPlan] = Field(None, description="Direct ExperimentPlan object payload")
    plan_id: Optional[str] = Field(None, description="ID of an existing experiment plan")
    hypothesis: Optional[ScientificHypothesis] = Field(None, description="Direct ScientificHypothesis object payload")
    report: Optional[GenomeReportResponse] = Field(None, description="Raw GenomeReportResponse JSON object")


class ExecuteResponse(BaseModel):
    """Response DTO for POST /autoscientist/execute."""
    dataset_id: Optional[UUID] = Field(None, description="UUID of the analyzed dataset")
    plan_id: str = Field(..., description="ID of the underlying ExperimentPlan")
    execution_result: ExecutionResult = Field(..., description="Complete ExecutionResult object")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

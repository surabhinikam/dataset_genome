"""
backend/app/orchestrator/models.py — Pydantic v2 Models for Orchestrator Engine.

Defines ExecutionReport and RunConfig objects.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.orchestrator.state_machine import ExecutionState


class ExecutionReport(BaseModel):
    """
    Master Execution Report returned by DatasetGenomeEngine.run().
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    execution_id: str = Field(..., description="Unique execution run ID")
    dataset_version: str = Field(..., description="Target dataset version tag")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Overall composite adaptive dataset score")
    training_status: str = Field(..., description="AutoScientist training/benchmark status")
    publication_status: str = Field(..., description="Publication & Open Source readiness status")
    execution_time_seconds: float = Field(..., ge=0.0, description="Total execution duration in seconds")
    errors: List[str] = Field(default_factory=list, description="Captured pipeline execution errors")
    warnings: List[str] = Field(default_factory=list, description="Captured pipeline warnings")
    generated_artifacts: List[str] = Field(default_factory=list, description="List of generated output file paths")
    final_state: ExecutionState = Field(..., description="Final state machine state (COMPLETED or FAILED)")
    completed_at: datetime = Field(default_factory=datetime.utcnow, description="Run completion timestamp")

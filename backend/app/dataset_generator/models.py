"""
backend/app/dataset_generator/models.py — Pydantic v2 Schemas for Dataset Generator.

Defines ScientificReasoningRecord and supporting dataset generator models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DifficultyLevel(str, Enum):
    """Scientific reasoning problem difficulty level."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ScientificReasoningRecord(BaseModel):
    """
    Canonical Pydantic v2 record model representing a single scientific reasoning benchmark sample.
    
    Contains the full 16-field scientific reasoning lineage from observation to conclusion.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: str = Field(..., description="Unique record identifier slug (e.g. rec-agri-001)")
    domain: str = Field(..., description="Target scientific domain (e.g. Agriculture, Medicine)")
    difficulty: str = Field("medium", description="Problem difficulty: easy, medium, or hard")
    prompt: str = Field(..., description="User prompt or benchmark query statement")
    context: str = Field(..., description="Background scientific domain context and baseline metrics")
    observation: str = Field(..., description="Empirical scientific observation or anomaly detected")
    identified_problem: str = Field(..., description="Core data or physical problem identified")
    research_gap: str = Field(..., description="Unresolved scientific research gap or flaw")
    primary_hypothesis: str = Field(..., description="Primary testable and falsifiable scientific hypothesis claim")
    alternative_hypothesis: str = Field(..., description="Alternative or counter hypothesis claim")
    experiment_design: str = Field(..., description="Controlled experimental setup and mutation procedure")
    control_variables: List[str] = Field(default_factory=list, description="List of held constant control variables")
    evaluation_metrics: List[str] = Field(default_factory=list, description="Target evaluation metrics (e.g. f1_score, yield_delta)")
    expected_result: str = Field(..., description="Anticipated quantitative and qualitative experimental result")
    failure_cases: List[str] = Field(default_factory=list, description="Identified failure modes or edge cases")
    scientific_conclusion: str = Field(..., description="Final synthesized scientific conclusion and recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")


class DatasetExportResult(BaseModel):
    """Output summary returned after exporting records to JSONL."""
    output_path: str = Field(..., description="Absolute or relative file path of the exported JSONL")
    total_records: int = Field(..., ge=0, description="Total count of exported records")
    domain: str = Field(..., description="Target domain of the exported batch")
    exported_at: datetime = Field(default_factory=datetime.utcnow, description="Export timestamp")

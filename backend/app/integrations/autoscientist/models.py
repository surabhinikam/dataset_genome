"""
backend/app/integrations/autoscientist/models.py — Pydantic v2 Models for AutoScientist Integration.

Defines MappedDataset, ExperimentEvaluationReport, DatasetFeedbackReport,
AutoScientistJobStatus, and AutoScientistResult.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AutoScientistJobStatus(str, Enum):
    """Job execution status in AutoScientist system."""
    PREPARED = "PREPARED"
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AutoScientistSampleItem(BaseModel):
    """Mapped individual scientific sample structured for AutoScientist ingestion."""
    record_id: str = Field(..., description="Unique specimen ID")
    domain: str = Field(..., description="Scientific domain")
    difficulty: str = Field(..., description="Problem difficulty level")
    reasoning_chain: Dict[str, Any] = Field(..., description="10-point reasoning chain dictionary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Auxiliary sample metadata")


class MappedDataset(BaseModel):
    """MODULE 1 output: Dataset converted and mapped for AutoScientist ingestion."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_version: str = Field(..., description="Source dataset version slug")
    samples: List[AutoScientistSampleItem] = Field(default_factory=list, description="List of mapped samples")
    total_samples: int = Field(..., ge=0, description="Total count of mapped samples")
    schema_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata schema details")
    mapped_at: datetime = Field(default_factory=datetime.utcnow, description="Mapping timestamp")


class ExperimentEvaluationReport(BaseModel):
    """MODULE 3 output: Evaluation extracted from AutoScientist benchmark runs."""
    experiment_id: str = Field(..., description="Unique AutoScientist experiment ID")
    experiment_success: bool = Field(..., description="Boolean flag: True if benchmark experiment completed successfully")
    reasoning_quality_score: float = Field(..., ge=0.0, le=100.0, description="Evaluated reasoning quality score [0..100]")
    hypothesis_accuracy: float = Field(..., ge=0.0, le=1.0, description="Accuracy of primary scientific hypothesis predictions")
    failure_analysis: List[str] = Field(default_factory=list, description="List of detected model failure modes")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall AutoScientist model confidence score")
    scientific_metrics: Dict[str, float] = Field(default_factory=dict, description="Domain-specific evaluation metrics (e.g. f1, rmse)")
    domain_accuracies: Dict[str, float] = Field(default_factory=dict, description="Accuracy breakdown per scientific domain")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")


class FeedbackRecommendationItem(BaseModel):
    """Individual feedback recommendation returned to Dataset Genome."""
    recommendation_id: str = Field(..., description="Unique recommendation ID")
    target_domain: str = Field(..., description="Target scientific domain requiring dataset enhancement")
    action: str = Field(..., description="Recommended action (e.g. Generate more Genomics samples, Increase experiment diversity)")
    reason: str = Field(..., description="Detailed justification based on AutoScientist performance weakness")
    priority: int = Field(..., ge=1, description="1-indexed priority rank")
    estimated_sample_count: int = Field(..., ge=1, description="Recommended number of new samples to generate")


class DatasetFeedbackReport(BaseModel):
    """MODULE 4 output: Feedback report connecting AutoScientist evaluation back to Dataset Genome."""
    weak_domains: List[str] = Field(default_factory=list, description="List of domains where model performed below threshold")
    recommended_dataset_actions: List[FeedbackRecommendationItem] = Field(default_factory=list, description="Actionable feedback recommendations")
    priority_level: str = Field(..., description="Overall feedback urgency: HIGH, MEDIUM, LOW")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Feedback generation timestamp")


class AutoScientistResult(BaseModel):
    """
    Final Composite Output of AutoScientist Integration Layer.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_id: str = Field(..., description="Unique AutoScientist execution job ID")
    training_status: AutoScientistJobStatus = Field(..., description="Job status in AutoScientist")
    experiment_results: Dict[str, Any] = Field(default_factory=dict, description="Raw collected experiment results payload")
    evaluation: ExperimentEvaluationReport = Field(..., description="Report from Module 3: Experiment Evaluator")
    feedback: DatasetFeedbackReport = Field(..., description="Report from Module 4: Feedback Engine")
    recommended_dataset_actions: List[str] = Field(default_factory=list, description="High-level human-readable dataset improvement actions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Integration completion timestamp")

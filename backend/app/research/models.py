"""
backend/app/research/models.py — Pydantic v2 Schemas for Autonomous Research Workflow.

Defines models for research iterations, score progression, version lineage tracking,
improvement requests, stopping criteria, and full research reports.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StoppingCriteriaConfig(BaseModel):
    """Configurable stopping criteria rules for the research workflow loop."""

    max_iterations: int = Field(3, description="Maximum number of research loop iterations.")
    target_adaptive_score: float = Field(85.0, description="Target adaptive dataset score to stop.")
    target_evaluation_score: float = Field(90.0, description="Target AutoScientist evaluation accuracy to stop.")
    min_improvement_threshold: float = Field(0.5, description="Minimum score delta improvement required to continue.")


class FailurePattern(BaseModel):
    """Pattern describing why the model underperformed during benchmark evaluation."""

    category: str = Field(..., description="Failure category e.g. 'Weak Domain', 'Low Hypothesis Diversity'.")
    description: str = Field(..., description="Explanation of failure mechanism.")
    severity: str = Field("MEDIUM", description="Severity: CRITICAL, HIGH, MEDIUM, LOW.")
    affected_domain: Optional[str] = Field(None, description="Domain impacted by failure pattern.")


class ResearchRecommendation(BaseModel):
    """Actionable dataset improvement recommendation formulated by ImprovementPlanner."""

    recommendation_id: str = Field(..., description="Unique recommendation ID.")
    action_type: str = Field(..., description="Action e.g. 'INCREASE_SAMPLES', 'BALANCE_DOMAINS', 'HARDER_REASONING'.")
    target_domain: str = Field(..., description="Target domain for action.")
    rationale: str = Field(..., description="Scientific rationale for recommendation.")
    expected_score_gain: float = Field(2.5, description="Expected adaptive score gain.")


class ResearchImprovementRequest(BaseModel):
    """Feedback request converting recommendations into dataset evolution instructions."""

    request_id: str = Field(..., description="Unique request ID.")
    from_version: str = Field(..., description="Source dataset version tag e.g. 'v1.0'.")
    to_version: str = Field(..., description="Target dataset version tag e.g. 'v2.0'.")
    applied_recommendations: List[ResearchRecommendation] = Field(default_factory=list)
    expected_improvement: float = Field(0.0, description="Cumulative expected score improvement.")
    observed_improvement: Optional[float] = Field(None, description="Actual observed score improvement.")


class IterationRecord(BaseModel):
    """Record of a single research iteration step within the closed loop."""

    iteration_index: int = Field(..., description="1-indexed iteration number.")
    dataset_version: str = Field(..., description="Version tag for this iteration.")
    sample_count: int = Field(..., description="Number of scientific reasoning records.")
    adaptive_score: float = Field(..., description="Adaptive dataset score [0..100].")
    hypothesis_accuracy: float = Field(..., description="AutoScientist hypothesis accuracy [0..100].")
    reasoning_quality: float = Field(..., description="Reasoning density quality score [0..100].")
    publication_status: str = Field("READY", description="Publication readiness status.")
    failure_patterns: List[FailurePattern] = Field(default_factory=list)
    applied_recommendations: List[ResearchRecommendation] = Field(default_factory=list)
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class VersionLineageRecord(BaseModel):
    """Lineage tracker tracking metrics across dataset versions (v1 -> v2 -> v3)."""

    version_tag: str = Field(..., description="Version tag e.g. 'v1.0-adaptive'.")
    adaptive_score: float = Field(..., description="Adaptive score.")
    training_score: float = Field(..., description="AutoScientist accuracy score.")
    reasoning_quality: float = Field(..., description="Reasoning quality score.")
    publication_status: str = Field(..., description="Publication status.")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResearchWorkflowReport(BaseModel):
    """Complete research workflow report output (research_report.json / research_report.md)."""

    research_id: str = Field(..., description="Unique research workflow ID.")
    total_iterations: int = Field(..., description="Total iterations executed.")
    stopping_reason: str = Field(..., description="Reason why research loop stopped.")
    initial_version: str = Field(..., description="Starting dataset version tag.")
    final_version: str = Field(..., description="Final evolved dataset version tag.")
    initial_adaptive_score: float = Field(..., description="Starting adaptive score.")
    final_adaptive_score: float = Field(..., description="Final adaptive score.")
    initial_accuracy: float = Field(..., description="Starting hypothesis evaluation accuracy.")
    final_accuracy: float = Field(..., description="Final hypothesis evaluation accuracy.")
    score_delta: float = Field(..., description="Total adaptive score improvement.")
    iterations: List[IterationRecord] = Field(default_factory=list)
    version_lineage: List[VersionLineageRecord] = Field(default_factory=list)
    remaining_weaknesses: List[str] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=datetime.utcnow)

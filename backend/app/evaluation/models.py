"""
backend/app/evaluation/models.py — Pydantic v2 Models for Benchmark & Evaluation Framework.

Defines schemas for dataset metrics, model training metrics, benchmark experiment run records,
Raw vs. Optimized comparisons, leaderboard entries, and full evaluation reports.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetMetrics(BaseModel):
    """Metrics assessing internal dataset structure, quality, and diversity."""

    dataset_health: float = Field(..., ge=0.0, le=100.0, description="Overall dataset health score [0..100].")
    knowledge_coverage: float = Field(..., ge=0.0, le=100.0, description="Knowledge graph coverage score [0..100].")
    reasoning_quality: float = Field(..., ge=0.0, le=100.0, description="Scientific reasoning quality score [0..100].")
    experiment_diversity: float = Field(..., ge=0.0, le=100.0, description="Experiment design diversity score [0..100].")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Adaptive Data Engine composite score [0..100].")


class ModelTrainingMetrics(BaseModel):
    """Metrics assessing downstream model performance trained on benchmark dataset."""

    training_accuracy: float = Field(..., ge=0.0, le=100.0, description="Hypothesis accuracy percentage [0..100].")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="Macro F1 classification/reasoning score [0..1.0].")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score [0..1.0].")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score [0..1.0].")
    inference_success_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of successfully executed benchmark inferences [0..100].")


class BenchmarkRunRecord(BaseModel):
    """Single benchmark experiment execution record (Raw vs. Optimized dataset run)."""

    experiment_id: str = Field(..., description="Unique experiment run ID.")
    dataset_version: str = Field(..., description="Dataset version tag e.g. 'v1.0-raw', 'v2.0-adaptive'.")
    dataset_type: str = Field(..., description="Dataset type: 'RAW' or 'OPTIMIZED'.")
    domain: str = Field(..., description="Scientific domain evaluated e.g. 'Agriculture', 'Oncology'.")
    model_version: str = Field("AutoScientist-v1.0", description="Evaluated downstream model identifier.")
    sample_count: int = Field(..., ge=1, description="Number of dataset samples evaluated.")
    execution_time_seconds: float = Field(..., ge=0.0, description="Benchmark execution duration in seconds.")
    dataset_metrics: DatasetMetrics = Field(..., description="Evaluated dataset quality metrics.")
    model_metrics: ModelTrainingMetrics = Field(..., description="Evaluated downstream model metrics.")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Artifact file paths produced during run.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp.")


class ComparisonResult(BaseModel):
    """Comparative analysis comparing Raw Dataset vs Optimized Dataset benchmark runs."""

    raw_experiment_id: str = Field(..., description="Raw dataset experiment run ID.")
    optimized_experiment_id: str = Field(..., description="Optimized dataset experiment run ID.")
    domain: str = Field(..., description="Target scientific domain.")
    dataset_version_from: str = Field(..., description="Source dataset version tag.")
    dataset_version_to: str = Field(..., description="Optimized dataset version tag.")

    # Metric Deltas
    health_delta: float = Field(..., description="Dataset health score absolute delta.")
    health_improvement_pct: float = Field(..., description="Dataset health percentage improvement.")

    coverage_delta: float = Field(..., description="Knowledge coverage absolute delta.")
    coverage_improvement_pct: float = Field(..., description="Knowledge coverage percentage improvement.")

    reasoning_delta: float = Field(..., description="Reasoning quality absolute delta.")
    reasoning_improvement_pct: float = Field(..., description="Reasoning quality percentage improvement.")

    adaptive_score_delta: float = Field(..., description="Adaptive score absolute delta.")
    adaptive_score_improvement_pct: float = Field(..., description="Adaptive score percentage improvement.")

    accuracy_delta: float = Field(..., description="Downstream training accuracy absolute delta.")
    accuracy_improvement_pct: float = Field(..., description="Training accuracy percentage improvement.")

    f1_delta: float = Field(..., description="F1 score absolute delta.")
    f1_improvement_pct: float = Field(..., description="F1 score percentage improvement.")

    overall_improvement_score: float = Field(..., description="Weighted composite improvement score delta.")


class LeaderboardEntry(BaseModel):
    """Ranked entry in the Dataset Genome Evaluation Leaderboard."""

    rank: int = Field(..., ge=1, description="1-indexed leaderboard rank position.")
    dataset_version: str = Field(..., description="Dataset version tag.")
    dataset_type: str = Field(..., description="Dataset type ('RAW' or 'OPTIMIZED').")
    domain: str = Field(..., description="Evaluated domain or 'All Domains'.")
    model_version: str = Field(..., description="Evaluated downstream model version.")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Adaptive dataset score.")
    training_score: float = Field(..., ge=0.0, le=100.0, description="Model training accuracy score.")
    publication_score: float = Field(..., ge=0.0, le=100.0, description="Publication readiness score.")
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Overall weighted composite evaluation score.")


class EvaluationReport(BaseModel):
    """Comprehensive evaluation report output (evaluation_report.json / evaluation_report.md)."""

    eval_id: str = Field(..., description="Unique evaluation report execution ID.")
    total_experiments: int = Field(..., ge=0, description="Total benchmark experiments evaluated.")
    best_dataset_version: str = Field(..., description="Top-performing dataset version tag.")
    best_model_version: str = Field(..., description="Top-performing model identifier.")
    overall_improvement_pct: float = Field(..., description="Average composite percentage improvement across all comparisons.")
    comparisons: List[ComparisonResult] = Field(default_factory=list, description="Raw vs Optimized comparative benchmark results.")
    leaderboard: List[LeaderboardEntry] = Field(default_factory=list, description="Ranked evaluation leaderboard entries.")
    score_progression: Dict[str, List[float]] = Field(default_factory=dict, description="Score progression timelines by dataset version.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable insights derived from evaluation metrics.")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp.")

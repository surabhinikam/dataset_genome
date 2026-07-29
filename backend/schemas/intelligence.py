"""
schemas/intelligence.py — Pydantic schemas for Dataset Genome Analysis & Profilers.

Defines all metrics, issue payloads, correlation matrices, and the complete
Genome Report returned by POST /analyze.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class DatasetIssue(BaseModel):
    """Represents an issue detected by one of the profilers."""
    id: str = Field(..., description="Unique slug for the issue")
    title: str = Field(..., description="Short summary of the issue")
    description: str = Field(..., description="Detailed explanation of the flaw")
    severity: IssueSeverity = Field(..., description="Severity level: critical, warning, or info")
    column_name: Optional[str] = Field(None, description="Affected column name, if applicable")
    recommendation: str = Field(..., description="Actionable fix recommendation")


class CompletenessMetrics(BaseModel):
    """Metrics calculated by the Completeness Profiler."""
    score: float = Field(..., ge=0.0, le=100.0, description="Completeness score (0-100)")
    total_cells: int = Field(..., ge=0)
    missing_cells: int = Field(..., ge=0)
    missing_cell_ratio: float = Field(..., ge=0.0, le=1.0)
    complete_row_ratio: float = Field(..., ge=0.0, le=1.0)
    column_missing_rates: Dict[str, float] = Field(default_factory=dict)


class ConsistencyMetrics(BaseModel):
    """Metrics calculated by the Consistency Profiler."""
    score: float = Field(..., ge=0.0, le=100.0, description="Consistency score (0-100)")
    total_rows: int = Field(..., ge=0)
    duplicate_rows: int = Field(..., ge=0)
    duplicate_ratio: float = Field(..., ge=0.0, le=1.0)
    type_uniformity_scores: Dict[str, float] = Field(default_factory=dict)
    mixed_type_columns: List[str] = Field(default_factory=list)


class BalanceMetrics(BaseModel):
    """Metrics calculated by the Balance Profiler."""
    score: float = Field(..., ge=0.0, le=100.0, description="Balance score (0-100)")
    categorical_entropy: Dict[str, float] = Field(default_factory=dict, description="Shannon entropy per column")
    majority_class_ratios: Dict[str, float] = Field(default_factory=dict)
    imbalanced_columns: List[str] = Field(default_factory=list)


class ColumnOutlierDetail(BaseModel):
    """Outlier details for a single numeric column calculated via IQR method."""
    q1: float
    q3: float
    iqr: float
    lower_bound: float
    upper_bound: float
    outlier_count: int
    outlier_ratio: float


class NoiseMetrics(BaseModel):
    """Metrics calculated by the Noise Profiler using IQR method."""
    score: float = Field(..., ge=0.0, le=100.0, description="Noise / Outlier score (0-100)")
    total_outliers: int = Field(..., ge=0)
    outlier_ratio: float = Field(..., ge=0.0, le=1.0)
    column_outliers: Dict[str, ColumnOutlierDetail] = Field(default_factory=dict)


class CorrelationPair(BaseModel):
    """Pair of numerical columns with high Pearson correlation."""
    column_1: str
    column_2: str
    coefficient: float = Field(..., ge=-1.0, le=1.0)


class CorrelationMetrics(BaseModel):
    """Metrics calculated by the Correlation Profiler."""
    score: float = Field(..., ge=0.0, le=100.0, description="Correlation score (0-100)")
    numeric_columns: List[str] = Field(default_factory=list)
    high_correlation_pairs: List[CorrelationPair] = Field(default_factory=list)
    matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Pairwise Pearson matrix")


class FeatureQualityMetrics(BaseModel):
    """Metrics calculated by the Feature Quality Profiler."""
    score: float = Field(..., ge=0.0, le=100.0, description="Feature Quality score (0-100)")
    total_features: int = Field(..., ge=0)
    constant_columns: List[str] = Field(default_factory=list, description="Columns with zero variance")
    low_variance_columns: List[str] = Field(default_factory=list)
    id_like_columns: List[str] = Field(default_factory=list, description="Columns with 100% unique string IDs")


class HealthScoreResult(BaseModel):
    """Overall dataset Health Score and grade classification."""
    overall_score: float = Field(..., ge=0.0, le=100.0)
    grade: str = Field(..., description="Grade: Excellent, Good, Fair, Poor")
    grade_color: str = Field(..., description="HEX/Tailwind color token for UI rendering")
    breakdown: Dict[str, float] = Field(..., description="Dimensional scores breakdown")


class GenomeReportResponse(BaseModel):
    """
    Complete Genome Report JSON returned by POST /analyze.
    """
    dataset_id: UUID
    filename: str
    num_rows: int
    num_cols: int
    column_names: List[str]
    health_score: HealthScoreResult
    completeness: CompletenessMetrics
    consistency: ConsistencyMetrics
    balance: BalanceMetrics
    noise: NoiseMetrics
    correlation: CorrelationMetrics
    feature_quality: FeatureQualityMetrics
    issues: List[DatasetIssue]
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

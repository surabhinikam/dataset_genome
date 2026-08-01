"""
backend/app/evaluation — Benchmark & Evaluation Framework for Dataset Genome.

Evaluates dataset quality and downstream model performance across Raw vs. Optimized datasets,
scientific domains, and dataset versions.
"""

from app.evaluation.benchmark import BenchmarkRunner
from app.evaluation.comparator import DatasetComparator
from app.evaluation.config import DEFAULT_EVALUATION_CONFIG, EvaluationConfig
from app.evaluation.experiments import ExperimentTracker
from app.evaluation.leaderboard import EvaluationLeaderboard
from app.evaluation.metrics import MetricsEngine
from app.evaluation.models import (
    BenchmarkRunRecord,
    ComparisonResult,
    DatasetMetrics,
    EvaluationReport,
    LeaderboardEntry,
    ModelTrainingMetrics,
)
from app.evaluation.report import export_evaluation_report_json, export_evaluation_report_markdown

__all__ = [
    "BenchmarkRunner",
    "MetricsEngine",
    "DatasetComparator",
    "ExperimentTracker",
    "EvaluationLeaderboard",
    "EvaluationConfig",
    "DEFAULT_EVALUATION_CONFIG",
    "DatasetMetrics",
    "ModelTrainingMetrics",
    "BenchmarkRunRecord",
    "ComparisonResult",
    "LeaderboardEntry",
    "EvaluationReport",
    "export_evaluation_report_json",
    "export_evaluation_report_markdown",
]

"""
backend/app/dataset_intelligence — Dataset Intelligence Engine for Scientific Reasoning Datasets.

Analyzes JSONL scientific datasets and generates comprehensive DatasetAnalysisReport quality reports,
general statistics, reasoning coverage metrics, diversity metrics, and normalized health scores (0–100).
"""

from app.dataset_intelligence.analyzer import DatasetAnalyzer
from app.dataset_intelligence.models import (
    DatasetAnalysisReport,
    DatasetHealthScores,
    DiversityMetrics,
    GeneralStatistics,
    QualityMetrics,
    ReasoningCoverageMetrics,
)
from app.dataset_intelligence.report import export_report_json, export_report_markdown

__all__ = [
    "DatasetAnalyzer",
    "DatasetAnalysisReport",
    "GeneralStatistics",
    "ReasoningCoverageMetrics",
    "DiversityMetrics",
    "QualityMetrics",
    "DatasetHealthScores",
    "export_report_json",
    "export_report_markdown",
]

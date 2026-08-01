"""
backend/app/benchmark — Official Benchmark v1.0 Generation & Management System.

Provides official benchmark sample generation, validation, statistics calculation,
version lineage tracking, multi-format exports, and report exporters for Dataset Genome.
"""

from app.benchmark.exporter import BenchmarkExporter
from app.benchmark.generator import DIFFICULTY_LEVELS, SUPPORTED_DOMAINS, BenchmarkGenerator
from app.benchmark.manager import DatasetGenomeBenchmarkManager
from app.benchmark.models import (
    BenchmarkReport,
    BenchmarkSample,
    BenchmarkSampleBuilder,
    BenchmarkStatistics,
    BenchmarkVersionRecord,
    ValidationResult,
)
from app.benchmark.report import export_benchmark_report_json, export_benchmark_report_markdown
from app.benchmark.statistics import BenchmarkStatisticsEngine
from app.benchmark.validator import BenchmarkValidator
from app.benchmark.versioning import BenchmarkVersionManager

__all__ = [
    "DatasetGenomeBenchmarkManager",
    "BenchmarkGenerator",
    "BenchmarkValidator",
    "BenchmarkStatisticsEngine",
    "BenchmarkExporter",
    "BenchmarkVersionManager",
    "BenchmarkSample",
    "BenchmarkSampleBuilder",
    "BenchmarkStatistics",
    "ValidationResult",
    "BenchmarkVersionRecord",
    "BenchmarkReport",
    "SUPPORTED_DOMAINS",
    "DIFFICULTY_LEVELS",
    "export_benchmark_report_json",
    "export_benchmark_report_markdown",
]

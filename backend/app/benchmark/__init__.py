"""
backend/app/benchmark — Official Benchmark v1.0 Generation & Management System.

Provides official benchmark sample generation (template-based and LLM-powered),
validation, statistics calculation, version lineage tracking, multi-format exports,
and report exporters for Dataset Genome.
"""

from app.benchmark.dashboard_data import BenchmarkDashboardDataEngine
from app.benchmark.deduplicator import BenchmarkDeduplicator
from app.benchmark.diversity_engine import ScientificDiversityEngine
from app.benchmark.diversity_report import DatasetDiversityReporter
from app.benchmark.exporter import BenchmarkExporter
from app.benchmark.generator import DIFFICULTY_LEVELS, SUPPORTED_DOMAINS, BenchmarkGenerator
from app.benchmark.llm_generator import GenerationExhaustedError, LLMBenchmarkGenerator
from app.benchmark.manager import DatasetGenomeBenchmarkManager
from app.benchmark.models import (
    BenchmarkReport,
    BenchmarkSample,
    BenchmarkSampleBuilder,
    BenchmarkStatistics,
    BenchmarkVersionRecord,
    ValidationResult,
)
from app.benchmark.prompt_builder import BenchmarkPromptBuilder
from app.benchmark.quality_scorer import BenchmarkQualityScorer
from app.benchmark.report import export_benchmark_report_json, export_benchmark_report_markdown
from app.benchmark.response_parser import BenchmarkParseError, BenchmarkResponseParser
from app.benchmark.statistics import BenchmarkStatisticsEngine
from app.benchmark.validator import BenchmarkValidator
from app.benchmark.versioning import BenchmarkVersionManager

__all__ = [
    # Core
    "DatasetGenomeBenchmarkManager",
    "BenchmarkGenerator",
    "BenchmarkValidator",
    "BenchmarkStatisticsEngine",
    "BenchmarkExporter",
    "BenchmarkVersionManager",
    # Models
    "BenchmarkSample",
    "BenchmarkSampleBuilder",
    "BenchmarkStatistics",
    "ValidationResult",
    "BenchmarkVersionRecord",
    "BenchmarkReport",
    # Constants
    "SUPPORTED_DOMAINS",
    "DIFFICULTY_LEVELS",
    # Report helpers
    "export_benchmark_report_json",
    "export_benchmark_report_markdown",
    # Phase 11 — LLM Generation
    "LLMBenchmarkGenerator",
    "GenerationExhaustedError",
    "BenchmarkPromptBuilder",
    "BenchmarkResponseParser",
    "BenchmarkParseError",
    "BenchmarkDeduplicator",
    # Phase 12 — Production Quality & Diversity Engine
    "BenchmarkQualityScorer",
    "ScientificDiversityEngine",
    "DatasetDiversityReporter",
    "BenchmarkDashboardDataEngine",
]

"""
backend/app/dataset_generator — Dataset Generator for Scientific Reasoning Benchmark.

Provides Pydantic v2 models, template prompt seeds, generator engine, and JSONL exporters
for creating scientific reasoning datasets.
"""

from app.dataset_generator.exporters import JSONLExporter
from app.dataset_generator.generator import DatasetGenerator
from app.dataset_generator.models import (
    DatasetExportResult,
    DifficultyLevel,
    ScientificReasoningRecord,
)
from app.dataset_generator.templates import get_template_seed

__all__ = [
    "DatasetGenerator",
    "ScientificReasoningRecord",
    "DatasetExportResult",
    "JSONLExporter",
    "DifficultyLevel",
    "get_template_seed",
]

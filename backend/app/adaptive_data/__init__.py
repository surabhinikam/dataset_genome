"""
backend/app/adaptive_data — Adaptive Data Engine for Dataset Genome.

Core optimization layer that transforms raw/evolved scientific reasoning datasets into scientifically
validated, balanced, enriched, and training-ready datasets for AutoScientist and model fine-tuning.
"""

from app.adaptive_data.agents.balancer import DatasetBalancer
from app.adaptive_data.agents.cleaner import DatasetCleaner
from app.adaptive_data.agents.enricher import DatasetEnricher
from app.adaptive_data.agents.optimizer import DatasetOptimizer
from app.adaptive_data.agents.scorer import AdaptiveScorer
from app.adaptive_data.agents.validator import ScientificValidator
from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import (
    AdaptiveDataReport,
    BalanceReport,
    CleaningReport,
    EnrichmentReport,
    OptimizationPlan,
    TrainingReadyDataset,
    ValidationReport,
)
from app.adaptive_data.pipeline import AdaptiveDataPipeline
from app.adaptive_data.report import (
    export_adaptive_report_json,
    export_adaptive_report_markdown,
    export_training_jsonl,
)

__all__ = [
    "AdaptiveDataPipeline",
    "TrainingReadyDataset",
    "AdaptiveDataReport",
    "CleaningReport",
    "ValidationReport",
    "BalanceReport",
    "OptimizationPlan",
    "EnrichmentReport",
    "AdaptiveEngineConfig",
    "DEFAULT_CONFIG",
    "DatasetCleaner",
    "ScientificValidator",
    "DatasetBalancer",
    "DatasetOptimizer",
    "DatasetEnricher",
    "AdaptiveScorer",
    "export_adaptive_report_json",
    "export_adaptive_report_markdown",
    "export_training_jsonl",
]

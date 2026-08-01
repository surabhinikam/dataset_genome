"""
backend/app/evaluation/config.py — Configuration for Benchmark & Evaluation Framework.

Defines EvaluationConfig Pydantic model for default benchmark domains, metric weightings,
threshold targets, output artifact paths, and chart formatting rules.
"""

from pathlib import Path
from typing import Dict, List, Union
from pydantic import BaseModel, Field


class EvaluationConfig(BaseModel):
    """
    Configuration parameters for Dataset Genome Benchmark & Evaluation Framework.
    """

    default_domains: List[str] = Field(
        default_factory=lambda: ["Agriculture", "Oncology", "Genetics", "Clinical Trials"],
        description="Default scientific domains to include in benchmark experiments.",
    )
    sample_count_per_domain: int = Field(
        20,
        ge=5,
        description="Number of scientific reasoning records to generate per domain in benchmark runs.",
    )
    target_health_score: float = Field(
        85.0,
        ge=0.0,
        le=100.0,
        description="Target dataset health score threshold.",
    )
    target_accuracy_pct: float = Field(
        85.0,
        ge=0.0,
        le=100.0,
        description="Target downstream model training accuracy threshold.",
    )
    metric_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "dataset_health": 0.20,
            "knowledge_coverage": 0.20,
            "reasoning_quality": 0.20,
            "experiment_diversity": 0.15,
            "training_accuracy": 0.25,
        },
        description="Weights for calculating overall composite dataset evaluation score.",
    )
    output_dir: Path = Field(
        default_factory=lambda: Path("publication/reports/evaluation"),
        description="Directory path for saving evaluation artifacts and reports.",
    )


DEFAULT_EVALUATION_CONFIG = EvaluationConfig()

"""
backend/app/adaptive_data/config.py — Configuration & Thresholds for Adaptive Data Engine.

Defines default quality thresholds, agent scoring weights, and training readiness criteria.
"""

from typing import Dict
from pydantic import BaseModel, Field


class AdaptiveEngineConfig(BaseModel):
    """Configuration settings and quality thresholds for Adaptive Data Engine agents."""

    # Cleaning thresholds
    min_prompt_length: int = Field(15, description="Minimum allowed character length for record prompt")
    min_context_length: int = Field(20, description="Minimum allowed character length for scientific context")
    
    # Validation thresholds
    min_control_variables: int = Field(1, description="Minimum required control variables")
    min_evaluation_metrics: int = Field(1, description="Minimum required evaluation metrics")

    # Balance targets
    target_hard_sample_ratio: float = Field(0.30, ge=0.0, le=1.0, description="Target minimum ratio of hard difficulty samples")
    max_domain_imbalance_ratio: float = Field(0.40, ge=0.0, le=1.0, description="Maximum allowed dominance ratio for a single domain")

    # Training readiness criteria
    readiness_score_threshold: float = Field(80.0, ge=0.0, le=100.0, description="Minimum overall adaptive score required for training readiness")
    max_allowed_logical_flaws: int = Field(0, description="Maximum allowed critical logical flaws in training dataset")

    # Scoring Weights for Overall Adaptive Score (sum = 1.0)
    score_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "cleaning": 0.15,
            "validation": 0.25,
            "coverage": 0.15,
            "balance": 0.15,
            "optimization": 0.15,
            "enrichment": 0.15,
        },
        description="Weights assigned to individual agent scores in composite adaptive score",
    )


DEFAULT_CONFIG = AdaptiveEngineConfig()

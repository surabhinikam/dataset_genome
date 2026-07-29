"""
backend/app/integrations/autoscientist — AutoScientist Integration Layer for Dataset Genome.

Acts as an extensible bridge between Dataset Genome optimized training datasets (TrainingReadyDataset)
and AutoScientist execution & reasoning engines.
"""

from app.integrations.autoscientist.adapter import AutoScientistAdapter
from app.integrations.autoscientist.client import BaseAutoScientistClient, MockAutoScientistClient
from app.integrations.autoscientist.config import DEFAULT_AUTOSCIENTIST_CONFIG, AutoScientistConfig
from app.integrations.autoscientist.evaluator import ExperimentEvaluator
from app.integrations.autoscientist.feedback import FeedbackEngine
from app.integrations.autoscientist.mapper import DatasetMapper
from app.integrations.autoscientist.models import (
    AutoScientistJobStatus,
    AutoScientistResult,
    DatasetFeedbackReport,
    ExperimentEvaluationReport,
    FeedbackRecommendationItem,
    MappedDataset,
)
from app.integrations.autoscientist.report import (
    export_autoscientist_result_json,
    export_autoscientist_result_markdown,
)

__all__ = [
    "AutoScientistAdapter",
    "DatasetMapper",
    "BaseAutoScientistClient",
    "MockAutoScientistClient",
    "ExperimentEvaluator",
    "FeedbackEngine",
    "AutoScientistResult",
    "MappedDataset",
    "ExperimentEvaluationReport",
    "DatasetFeedbackReport",
    "FeedbackRecommendationItem",
    "AutoScientistJobStatus",
    "AutoScientistConfig",
    "DEFAULT_AUTOSCIENTIST_CONFIG",
    "export_autoscientist_result_json",
    "export_autoscientist_result_markdown",
]

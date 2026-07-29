"""
backend/app/integrations/huggingface — Hugging Face Integration Platform for Dataset Genome.

Provides dataset publication preparation, model artifact packaging, dataset & model card generators (README.md),
version lineage management, metadata tracking, and hub upload abstraction.
"""

from app.integrations.huggingface.cards import DatasetCardGenerator, ModelCardGenerator
from app.integrations.huggingface.client import BaseHuggingFaceClient, MockHuggingFaceClient
from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.dataset import DatasetPublisher
from app.integrations.huggingface.datasets import HuggingFaceDatasetsWrapper
from app.integrations.huggingface.downloader import HuggingFaceDownloader
from app.integrations.huggingface.evaluate import HuggingFaceEvaluator, MetricRegistry
from app.integrations.huggingface.hub import HuggingFaceHubWrapper
from app.integrations.huggingface.metadata import MetadataManager
from app.integrations.huggingface.model import ModelPublisher
from app.integrations.huggingface.models import (
    DatasetPackage,
    DatasetVersionRecord,
    GenomeMetadata,
    ModelArtifactPackage,
    PublishingReport,
)
from app.integrations.huggingface.report import (
    export_publishing_report_json,
    export_publishing_report_markdown,
)
from app.integrations.huggingface.uploader import HuggingFaceUploader, ProductionHuggingFaceUploader
from app.integrations.huggingface.utils import TransformersLoader
from app.integrations.huggingface.versioning import VersionManager

__all__ = [
    "ProductionHuggingFaceUploader",
    "HuggingFaceUploader",
    "DatasetPublisher",
    "ModelPublisher",
    "DatasetCardGenerator",
    "ModelCardGenerator",
    "VersionManager",
    "MetadataManager",
    "BaseHuggingFaceClient",
    "MockHuggingFaceClient",
    "HuggingFaceHubWrapper",
    "HuggingFaceDatasetsWrapper",
    "HuggingFaceEvaluator",
    "HuggingFaceDownloader",
    "MetricRegistry",
    "TransformersLoader",
    "PublishingReport",
    "DatasetPackage",
    "ModelArtifactPackage",
    "DatasetVersionRecord",
    "GenomeMetadata",
    "HuggingFaceConfig",
    "DEFAULT_HF_CONFIG",
    "export_publishing_report_json",
    "export_publishing_report_markdown",
]

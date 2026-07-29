"""
backend/app/integrations/huggingface — Hugging Face Integration Platform for Dataset Genome.

Provides dataset publication preparation, model artifact packaging, dataset & model card generators (README.md),
version lineage management, metadata tracking, and hub upload abstraction.
"""

from app.integrations.huggingface.cards import DatasetCardGenerator, ModelCardGenerator
from app.integrations.huggingface.client import BaseHuggingFaceClient, MockHuggingFaceClient
from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.dataset import DatasetPublisher
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
from app.integrations.huggingface.uploader import HuggingFaceUploader
from app.integrations.huggingface.versioning import VersionManager

__all__ = [
    "HuggingFaceUploader",
    "DatasetPublisher",
    "ModelPublisher",
    "DatasetCardGenerator",
    "ModelCardGenerator",
    "VersionManager",
    "MetadataManager",
    "BaseHuggingFaceClient",
    "MockHuggingFaceClient",
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

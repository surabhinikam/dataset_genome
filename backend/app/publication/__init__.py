"""
backend/app/publication — Publication & Open Source Engine for Dataset Genome.

Converts Dataset Genome outputs into publication-ready open-source artifacts for Kaggle,
Hugging Face Hub, and Adaption Labs submission packages.
"""

from app.publication.artifacts.dataset_packager import DatasetPackager
from app.publication.artifacts.model_packager import ModelPackager
from app.publication.artifacts.report_packager import ReportPackager
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig
from app.publication.huggingface.card_generator import CardGenerator
from app.publication.huggingface.uploader import HuggingFaceUploader
from app.publication.kaggle.uploader import KaggleUploader
from app.publication.models import (
    DatasetArtifactPackage,
    HuggingFacePackage,
    KagglePackage,
    ModelArtifactPackage,
    PublicationReport,
    VersionRecord,
)
from app.publication.pipeline import PublicationPipeline
from app.publication.report import (
    export_publication_report_json,
    export_publication_report_markdown,
)

__all__ = [
    "PublicationPipeline",
    "PublicationReport",
    "DatasetArtifactPackage",
    "ModelArtifactPackage",
    "KagglePackage",
    "HuggingFacePackage",
    "VersionRecord",
    "PublicationConfig",
    "DEFAULT_PUBLICATION_CONFIG",
    "DatasetPackager",
    "ModelPackager",
    "ReportPackager",
    "CardGenerator",
    "HuggingFaceUploader",
    "KaggleUploader",
    "export_publication_report_json",
    "export_publication_report_markdown",
]

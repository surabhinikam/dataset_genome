"""
backend/app/publication/models.py — Pydantic v2 Models for Publication Engine.

Defines schemas for DatasetArtifactPackage, ModelArtifactPackage, VersionRecord,
KagglePackage, HuggingFacePackage, and PublicationReport.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DatasetArtifactPackage(BaseModel):
    """MODULE 1 output: Dataset Packager output files manifest."""
    dataset_version: str = Field(..., description="Dataset version slug")
    total_samples: int = Field(..., ge=0, description="Total sample count")
    dataset_final_path: str = Field(..., description="Path to dataset_final.json")
    dataset_statistics_path: str = Field(..., description="Path to dataset_statistics.json")
    schema_path: str = Field(..., description="Path to schema.json")
    metadata_path: str = Field(..., description="Path to metadata.json")
    dataset_summary_path: str = Field(..., description="Path to dataset_summary.md")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Package creation timestamp")


class ModelArtifactPackage(BaseModel):
    """MODULE 2 output: Model Packager output files manifest."""
    model_version: str = Field(..., description="Model version tag")
    architecture: str = Field(..., description="Model architecture slug")
    model_metadata_path: str = Field(..., description="Path to model_metadata.json")
    training_summary_path: str = Field(..., description="Path to training_summary.md")
    evaluation_path: str = Field(..., description="Path to evaluation.json")
    weights_manifest_path: str = Field(..., description="Path to weights_manifest.json")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Package creation timestamp")


class VersionRecord(BaseModel):
    """MODULE 5 output: Version Manager release record."""
    dataset_version: str = Field(..., description="Dataset version tag (e.g. v2.0)")
    model_version: str = Field(..., description="Model version tag (e.g. v1.0)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Release timestamp")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Adaptive dataset score")
    training_score: float = Field(..., ge=0.0, le=100.0, description="Model evaluation training score")
    commit_hash: str = Field(..., description="Git commit hash")
    changelog: str = Field(..., description="Changelog text")


class KagglePackage(BaseModel):
    """MODULE 6 output: Kaggle dataset bundle manifest."""
    dataset_slug: str = Field(..., description="Kaggle dataset slug")
    bundle_dir: str = Field(..., description="Path to kaggle bundle folder")
    metadata_json_path: str = Field(..., description="Path to dataset-metadata.json")
    readme_path: str = Field(..., description="Path to README.md")
    sample_count: int = Field(..., ge=0, description="Sample count")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Bundle creation timestamp")


class HuggingFacePackage(BaseModel):
    """MODULE 7 output: Hugging Face dataset & model repo bundle manifest."""
    repo_id: str = Field(..., description="Hugging Face repo ID")
    bundle_dir: str = Field(..., description="Path to huggingface bundle folder")
    dataset_card_path: str = Field(..., description="Path to dataset README.md")
    model_card_path: str = Field(..., description="Path to model README.md")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Bundle creation timestamp")


class PublicationReport(BaseModel):
    """
    MODULE 8 output: Publication Report summarizing open-source readiness.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    publication_id: str = Field(..., description="Unique publication report ID")
    dataset_ready: bool = Field(..., description="Boolean flag: True if dataset package is ready")
    model_ready: bool = Field(..., description="Boolean flag: True if model package is ready")
    hf_ready: bool = Field(..., description="Boolean flag: True if Hugging Face package is ready")
    kaggle_ready: bool = Field(..., description="Boolean flag: True if Kaggle package is ready")
    artifacts_generated: List[str] = Field(default_factory=list, description="List of generated output file paths")
    repository_structure: Dict[str, List[str]] = Field(default_factory=dict, description="Directory structure map")
    validation_status: Dict[str, str] = Field(default_factory=dict, description="Validation check results per target")
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Publication timestamp")

"""
backend/app/integrations/huggingface/models.py — Pydantic v2 Models for Hugging Face Integration.

Defines schemas for DatasetPackage, ModelArtifactPackage, DatasetVersionRecord,
GenomeMetadata, and PublishingReport.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GenomeMetadata(BaseModel):
    """MODULE 6 output: Metadata Manager tracking Dataset UUID, Model UUID, Author, and Pipeline info."""
    dataset_uuid: str = Field(..., description="Unique UUID for dataset package")
    model_uuid: str = Field(..., description="Unique UUID for model checkpoint package")
    version: str = Field(..., description="Canonical version tag (e.g. v3.0)")
    author: str = Field(..., description="Author attribution string")
    pipeline: str = Field("Dataset Genome Adaptive Data Pipeline", description="Pipeline name")
    generation_time: datetime = Field(default_factory=datetime.utcnow, description="Metadata creation timestamp")


class DatasetVersionRecord(BaseModel):
    """MODULE 5 output: Version Manager record tracking timestamp, changes, adaptive score, training score."""
    version_tag: str = Field(..., description="Version tag (e.g. v1.0, v2.0, v3.0)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Version release timestamp")
    changes: str = Field(..., description="Changelog description of modifications")
    adaptive_score: float = Field(..., ge=0.0, le=100.0, description="Dataset Adaptive Engine score")
    training_score: float = Field(..., ge=0.0, le=100.0, description="AutoScientist model evaluation score")


class DatasetPackage(BaseModel):
    """MODULE 1 output: Dataset Publisher package ready for Hugging Face Hub."""
    dataset_id: str = Field(..., description="Unique package ID")
    version_tag: str = Field(..., description="Version tag")
    total_samples: int = Field(..., ge=0, description="Total count of scientific records")
    dataset_files: List[str] = Field(default_factory=list, description="List of dataset file paths (e.g. train.jsonl, test.jsonl)")
    dataset_card_markdown: str = Field(..., description="Generated README.md dataset card text")
    schema_summary: Dict[str, Any] = Field(default_factory=dict, description="Dataset schema summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Package creation timestamp")


class ModelArtifactPackage(BaseModel):
    """MODULE 2 output: Model Publisher package ready for Hugging Face Hub."""
    model_id: str = Field(..., description="Unique model artifact ID")
    model_version: str = Field(..., description="Model version tag")
    architecture: str = Field(..., description="Model architecture (e.g. Transformer-AutoScientist-v1)")
    checkpoint_path: str = Field(..., description="Path to checkpoint weights or metadata file")
    evaluation_metrics: Dict[str, float] = Field(default_factory=dict, description="Evaluation metric scores (e.g. accuracy, f1)")
    model_card_markdown: str = Field(..., description="Generated README.md model card text")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Artifact creation timestamp")


class PublishingReport(BaseModel):
    """
    Final Output of Hugging Face Integration Platform.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    publication_id: str = Field(..., description="Unique publication report ID")
    dataset_version: str = Field(..., description="Published dataset version tag")
    model_version: str = Field(..., description="Published model version tag")
    artifacts: List[str] = Field(default_factory=list, description="List of generated publication artifact file paths")
    cards_generated: List[str] = Field(default_factory=list, description="List of generated README.md card names")
    ready_for_publish: bool = Field(..., description="Boolean flag: True if dataset & model packages pass validation")
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Publication timestamp")

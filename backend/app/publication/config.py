"""
backend/app/publication/config.py — Publication Engine Configuration.

Defines target directory paths, licenses, organization IDs, and release options.
"""

from pathlib import Path
from pydantic import BaseModel, Field


class PublicationConfig(BaseModel):
    """Configuration settings for Publication & Open Source Engine."""

    base_output_dir: str = Field("publication", description="Base root directory for generated publication artifacts")
    dataset_dir: str = Field("publication/dataset", description="Path for formatted dataset artifacts")
    model_dir: str = Field("publication/model", description="Path for formatted model artifacts")
    kaggle_dir: str = Field("publication/kaggle", description="Path for Kaggle release bundle")
    huggingface_dir: str = Field("publication/huggingface", description="Path for Hugging Face release bundle")
    reports_dir: str = Field("publication/reports", description="Path for publication evaluation reports")
    release_dir: str = Field("publication/release", description="Path for final compressed submission package")

    default_license: str = Field("apache-2.0", description="Default open-source license")
    organization: str = Field("dataset-genome", description="Default publishing organization")
    author: str = Field("Dataset Genome Core Team", description="Default author attribution")


DEFAULT_PUBLICATION_CONFIG = PublicationConfig()

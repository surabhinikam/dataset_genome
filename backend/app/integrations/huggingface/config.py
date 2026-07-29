"""
backend/app/integrations/huggingface/config.py — Hugging Face Integration Configuration.

Defines repository organization defaults, licenses, authors, and hub publication settings.
"""

from pydantic import BaseModel, Field


class HuggingFaceConfig(BaseModel):
    """Configuration settings for Hugging Face Integration Platform."""

    organization: str = Field("dataset-genome", description="Default Hugging Face organization or user ID")
    dataset_repo_name: str = Field("scientific-reasoning-benchmark", description="Default Hugging Face dataset repository name")
    model_repo_name: str = Field("autoscientist-reasoning-v1", description="Default Hugging Face model repository name")
    default_license: str = Field("apache-2.0", description="Default open-source software/dataset license")
    default_author: str = Field("Dataset Genome Core Team", description="Default author attribution")
    enable_mock_hub: bool = Field(True, description="Enable mock hub execution layer for offline publishing & testing")


DEFAULT_HF_CONFIG = HuggingFaceConfig()

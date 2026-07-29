"""
backend/app/integrations/huggingface/client.py — Hugging Face Client Abstraction.

Provides abstract BaseHuggingFaceClient interface and MockHuggingFaceClient implementation
for Hugging Face Hub repository interactions.
"""

from abc import ABC, abstractmethod
import logging
from typing import List, Optional

from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.models import DatasetPackage, ModelArtifactPackage

logger = logging.getLogger("dataset_genome.integrations.huggingface.client")


class BaseHuggingFaceClient(ABC):
    """
    Abstract Hugging Face Hub API client interface.
    """

    @abstractmethod
    def validate_package(self, package: DatasetPackage) -> bool:
        """Validate dataset package before uploading."""
        pass

    @abstractmethod
    def publish_dataset(self, package: DatasetPackage) -> str:
        """Publish dataset package to Hugging Face Hub."""
        pass

    @abstractmethod
    def publish_model(self, package: ModelArtifactPackage) -> str:
        """Publish model checkpoint package to Hugging Face Hub."""
        pass


class MockHuggingFaceClient(BaseHuggingFaceClient):
    """
    Mock implementation of BaseHuggingFaceClient for offline execution & testing.
    """

    def __init__(self, config: HuggingFaceConfig = DEFAULT_HF_CONFIG) -> None:
        self.config = config

    def validate_package(self, package: DatasetPackage) -> bool:
        """Validate dataset package schema and file integrity."""
        logger.info(f"Mock Client validating DatasetPackage '{package.dataset_id}'...")
        return package.total_samples > 0 and len(package.dataset_card_markdown) > 0

    def publish_dataset(self, package: DatasetPackage) -> str:
        """Publish dataset package (simulated)."""
        repo_url = f"https://huggingface.co/datasets/{self.config.organization}/{self.config.dataset_repo_name}"
        logger.info(f"Mock Client publishing dataset to '{repo_url}' (Version: {package.version_tag})...")
        return repo_url

    def publish_model(self, package: ModelArtifactPackage) -> str:
        """Publish model artifact package (simulated)."""
        repo_url = f"https://huggingface.co/models/{self.config.organization}/{self.config.model_repo_name}"
        logger.info(f"Mock Client publishing model to '{repo_url}' (Version: {package.model_version})...")
        return repo_url

"""
backend/app/integrations/huggingface/metadata.py — MODULE 6: Metadata Manager.

Generates and manages comprehensive Dataset Genome metadata tracking Dataset UUID, Model UUID,
Version, Author, Pipeline name, and Generation timestamps.
"""

import logging
import uuid
from typing import Optional

from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.models import GenomeMetadata

logger = logging.getLogger("dataset_genome.integrations.huggingface.metadata")


class MetadataManager:
    """
    MODULE 6 — Metadata Manager.
    
    Generates unique UUID identifiers and metadata manifests for Dataset Genome publication packages.
    """

    def __init__(self, config: HuggingFaceConfig = DEFAULT_HF_CONFIG) -> None:
        self.config = config

    def generate_metadata(
        self,
        version: str = "v3.0",
        author: Optional[str] = None,
        dataset_uuid: Optional[str] = None,
        model_uuid: Optional[str] = None,
    ) -> GenomeMetadata:
        """
        Generate a new GenomeMetadata manifest.
        """
        logger.info(f"Module 6 (MetadataManager) generating metadata manifest for version '{version}'...")

        ds_uuid = dataset_uuid or f"uuid-ds-{uuid.uuid4().hex[:12]}"
        mdl_uuid = model_uuid or f"uuid-mdl-{uuid.uuid4().hex[:12]}"
        aut = author or self.config.default_author

        metadata = GenomeMetadata(
            dataset_uuid=ds_uuid,
            model_uuid=mdl_uuid,
            version=version,
            author=aut,
            pipeline="Dataset Genome Adaptive Data Pipeline",
        )

        logger.info(f"Module 6 (MetadataManager) completed: Generated Dataset UUID '{ds_uuid}', Model UUID '{mdl_uuid}'.")
        return metadata

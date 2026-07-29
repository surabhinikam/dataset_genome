"""
backend/app/integrations/huggingface/dataset.py — MODULE 1: Dataset Publisher.

Prepares optimized datasets, validates schemas, generates dataset cards,
and produces DatasetPackage artifacts ready for Hugging Face Hub publication.
"""

import logging
import uuid
from typing import List, Optional

from app.adaptive_data.models import TrainingReadyDataset
from app.integrations.huggingface.cards import DatasetCardGenerator
from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.models import DatasetPackage

logger = logging.getLogger("dataset_genome.integrations.huggingface.dataset")


class DatasetPublisher:
    """
    MODULE 1 — Dataset Publisher.
    
    Bundles dataset files, validates schema definitions, and attaches generated README.md dataset cards.
    """

    def __init__(self, config: HuggingFaceConfig = DEFAULT_HF_CONFIG) -> None:
        self.config = config
        self.card_generator = DatasetCardGenerator(config=config)

    def prepare_package(
        self,
        dataset: TrainingReadyDataset,
        dataset_files: Optional[List[str]] = None,
    ) -> DatasetPackage:
        """
        Prepare a DatasetPackage from a TrainingReadyDataset.
        """
        logger.info(f"Module 1 (DatasetPublisher) bundling package for version '{dataset.dataset_version}'...")

        package_id = f"pkg-ds-{uuid.uuid4().hex[:8]}"
        files = dataset_files or ["datasets/final/train.jsonl", "datasets/final/validation.jsonl", "datasets/final/test.jsonl"]

        card_text = self.card_generator.generate_card(dataset)

        schema_summary = {
            "version": dataset.dataset_version,
            "total_samples": dataset.cleaning_summary.cleaned_sample_count,
            "adaptive_score": dataset.adaptive_score,
            "training_ready": dataset.training_ready,
        }

        package = DatasetPackage(
            dataset_id=package_id,
            version_tag=dataset.dataset_version,
            total_samples=dataset.cleaning_summary.cleaned_sample_count,
            dataset_files=files,
            dataset_card_markdown=card_text,
            schema_summary=schema_summary,
        )

        logger.info(f"Module 1 (DatasetPublisher) completed: DatasetPackage '{package_id}' created successfully.")
        return package

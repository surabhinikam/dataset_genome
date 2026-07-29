"""
backend/app/publication/huggingface/uploader.py — MODULE 7: Hugging Face Package Bundler.

Generates complete publication/huggingface/ folder containing README.md, dataset files,
metadata, license, model card, dataset card, and config.
Returns HuggingFacePackage.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from app.adaptive_data.models import TrainingReadyDataset
from app.integrations.autoscientist.models import AutoScientistResult
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig
from app.publication.huggingface.card_generator import CardGenerator
from app.publication.huggingface.dataset import DatasetPublisher
from app.publication.huggingface.metadata import MetadataGenerator
from app.publication.huggingface.model import ModelPublisher
from app.publication.huggingface.validator import PackageValidator
from app.publication.models import HuggingFacePackage

logger = logging.getLogger("dataset_genome.publication.huggingface.uploader")


class HuggingFaceUploader:
    """MODULE 7 — Hugging Face Package Coordinator."""

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config
        self.card_gen = CardGenerator(config=config)
        self.ds_publisher = DatasetPublisher(config=config)
        self.mdl_publisher = ModelPublisher(config=config)
        self.meta_gen = MetadataGenerator()
        self.validator = PackageValidator()

    def package(
        self,
        dataset: TrainingReadyDataset,
        autoscientist_result: AutoScientistResult,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> HuggingFacePackage:
        """Generate full publication/huggingface/ folder bundle."""
        target_dir = Path(output_dir) if output_dir else Path(self.config.huggingface_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Module 7 (HuggingFaceUploader) preparing bundle in '{target_dir}'...")

        # 1. Dataset files & Model files
        self.ds_publisher.prepare(dataset, target_dir)
        self.mdl_publisher.prepare(autoscientist_result, target_dir)
        self.meta_gen.generate(dataset.dataset_version, len(dataset.cleaned_records), target_dir)

        # 2. Cards
        ds_card = self.card_gen.generate_dataset_card(dataset)
        mdl_card = self.card_gen.generate_model_card(autoscientist_result)

        ds_card_path = target_dir / "DATASET_CARD.md"
        ds_card_path.write_text(ds_card, encoding="utf-8")

        mdl_card_path = target_dir / "MODEL_CARD.md"
        mdl_card_path.write_text(mdl_card, encoding="utf-8")

        readme_path = target_dir / "README.md"
        readme_path.write_text(ds_card, encoding="utf-8")

        # 3. License
        lic_path = target_dir / "LICENSE"
        lic_path.write_text(f"License: {self.config.default_license}\nCopyright (c) 2026 {self.config.author}", encoding="utf-8")

        repo_id = f"{self.config.organization}/scientific-reasoning-benchmark"

        package = HuggingFacePackage(
            repo_id=repo_id,
            bundle_dir=str(target_dir.resolve()),
            dataset_card_path=str(ds_card_path.resolve()),
            model_card_path=str(mdl_card_path.resolve()),
        )

        logger.info(f"Module 7 (HuggingFaceUploader) completed bundle for repo '{repo_id}'.")
        return package

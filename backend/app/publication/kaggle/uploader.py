"""
backend/app/publication/kaggle/uploader.py — MODULE 6: Kaggle Package Bundler.

Generates complete publication/kaggle/ folder containing dataset/, README.md,
dataset-metadata.json, license, sample_examples, and statistics.
Returns KagglePackage.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union

from app.adaptive_data.models import TrainingReadyDataset
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig
from app.publication.kaggle.metadata import KaggleMetadataGenerator
from app.publication.kaggle.package import KagglePackager
from app.publication.kaggle.validator import KaggleValidator
from app.publication.models import KagglePackage

logger = logging.getLogger("dataset_genome.publication.kaggle.uploader")


class KaggleUploader:
    """MODULE 6 — Kaggle Package Coordinator."""

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config
        self.meta_gen = KaggleMetadataGenerator()
        self.packager = KagglePackager()
        self.validator = KaggleValidator()

    def package(
        self,
        dataset: TrainingReadyDataset,
        dataset_slug: str = "dataset-genome-scientific-reasoning",
        output_dir: Optional[Union[str, Path]] = None,
    ) -> KagglePackage:
        """Generate full publication/kaggle/ folder bundle."""
        target_dir = Path(output_dir) if output_dir else Path(self.config.kaggle_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Module 6 (KaggleUploader) bundling Kaggle release in '{target_dir}'...")

        # 1. Internal package & dataset-metadata.json
        self.packager.prepare(dataset, target_dir)
        meta_path = self.meta_gen.generate(
            title="Dataset Genome Scientific Reasoning Benchmark",
            slug=dataset_slug,
            target_dir=target_dir,
        )

        # 2. README.md
        readme_md = (
            f"# Dataset Genome — Scientific Reasoning Benchmark (Kaggle Edition)\n\n"
            f"Official dataset distribution for Dataset Genome version `{dataset.dataset_version}`.\n"
            f"- Total Retained Samples: {dataset.cleaning_summary.cleaned_sample_count}\n"
            f"- Adaptive Score: {dataset.adaptive_score:.1f} / 100\n"
        )
        readme_path = target_dir / "README.md"
        readme_path.write_text(readme_md, encoding="utf-8")

        # 3. license
        lic_path = target_dir / "license"
        lic_path.write_text(f"License: {self.config.default_license}", encoding="utf-8")

        # 4. statistics
        stats = {
            "version": dataset.dataset_version,
            "samples": dataset.cleaning_summary.cleaned_sample_count,
            "domains": dataset.balance_summary.domain_distribution,
        }
        stats_path = target_dir / "statistics"
        stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

        package = KagglePackage(
            dataset_slug=dataset_slug,
            bundle_dir=str(target_dir.resolve()),
            metadata_json_path=str(meta_path.resolve()),
            readme_path=str(readme_path.resolve()),
            sample_count=dataset.cleaning_summary.cleaned_sample_count,
        )

        logger.info(f"Module 6 (KaggleUploader) completed Kaggle package.")
        return package

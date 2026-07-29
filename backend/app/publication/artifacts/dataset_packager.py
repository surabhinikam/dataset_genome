"""
backend/app/publication/artifacts/dataset_packager.py — MODULE 1: Dataset Packager.

Accepts TrainingReadyDataset and writes dataset_final.json, dataset_statistics.json,
schema.json, metadata.json, and dataset_summary.md into publication/dataset/.
Generates DatasetArtifactPackage.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union

from app.adaptive_data.models import TrainingReadyDataset
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig
from app.publication.models import DatasetArtifactPackage

logger = logging.getLogger("dataset_genome.publication.artifacts.dataset_packager")


class DatasetPackager:
    """
    MODULE 1 — Dataset Packager.
    """

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config

    def package(self, dataset: TrainingReadyDataset, output_dir: Optional[Union[str, Path]] = None) -> DatasetArtifactPackage:
        """
        Package TrainingReadyDataset into publication files.
        """
        target_dir = Path(output_dir) if output_dir else Path(self.config.dataset_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Module 1 (DatasetPackager) writing dataset artifacts to '{target_dir}'...")

        # 1. dataset_final.json
        final_records = [r.model_dump() for r in dataset.cleaned_records]
        ds_final_path = target_dir / "dataset_final.json"
        ds_final_path.write_text(json.dumps(final_records, indent=2, default=str), encoding="utf-8")

        # 2. dataset_statistics.json
        bs = dataset.balance_summary
        cs = dataset.cleaning_summary
        stats = {
            "version": dataset.dataset_version,
            "total_samples": cs.cleaned_sample_count,
            "adaptive_score": dataset.adaptive_score,
            "training_ready": dataset.training_ready,
            "domain_distribution": bs.domain_distribution,
            "difficulty_distribution": bs.difficulty_distribution,
            "experiment_type_distribution": bs.experiment_type_distribution,
        }
        ds_stats_path = target_dir / "dataset_statistics.json"
        ds_stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

        # 3. schema.json
        schema = {
            "title": "ScientificReasoningRecordSchema",
            "version": dataset.dataset_version,
            "fields": [
                "id", "domain", "difficulty", "prompt", "context", "observation",
                "identified_problem", "research_gap", "primary_hypothesis", "alternative_hypothesis",
                "experiment_design", "control_variables", "evaluation_metrics", "expected_result",
                "failure_cases", "scientific_conclusion"
            ],
            "reasoning_steps": 10,
        }
        schema_path = target_dir / "schema.json"
        schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

        # 4. metadata.json
        metadata = {
            "dataset_version": dataset.dataset_version,
            "author": self.config.author,
            "license": self.config.default_license,
            "created_at": dataset.created_at.isoformat(),
            "pipeline": "Dataset Genome Adaptive Engine",
        }
        meta_path = target_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        # 5. dataset_summary.md
        summary_md = (
            f"# Dataset Genome Summary (`{dataset.dataset_version}`)\n\n"
            f"- **Total Samples**: `{cs.cleaned_sample_count}`\n"
            f"- **Adaptive Score**: `{dataset.adaptive_score:.1f} / 100`\n"
            f"- **Training Readiness**: `{dataset.training_ready}`\n"
        )
        summary_path = target_dir / "dataset_summary.md"
        summary_path.write_text(summary_md, encoding="utf-8")

        package = DatasetArtifactPackage(
            dataset_version=dataset.dataset_version,
            total_samples=cs.cleaned_sample_count,
            dataset_final_path=str(ds_final_path.resolve()),
            dataset_statistics_path=str(ds_stats_path.resolve()),
            schema_path=str(schema_path.resolve()),
            metadata_path=str(meta_path.resolve()),
            dataset_summary_path=str(summary_path.resolve()),
        )

        logger.info(f"Module 1 (DatasetPackager) completed writing {cs.cleaned_sample_count} records.")
        return package

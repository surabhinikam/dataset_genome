"""
backend/app/publication/huggingface/dataset.py — Hugging Face Dataset Bundler.
"""

import json
import logging
from pathlib import Path

from app.adaptive_data.models import TrainingReadyDataset
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig

logger = logging.getLogger("dataset_genome.publication.huggingface.dataset")


class DatasetPublisher:
    """Prepares Hugging Face dataset folder files."""

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config

    def prepare(self, dataset: TrainingReadyDataset, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        records = [r.model_dump() for r in dataset.cleaned_records]
        
        with open(target_dir / "train.jsonl", "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, default=str) + "\n")

        return target_dir

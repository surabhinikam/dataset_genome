"""
backend/app/publication/huggingface/model.py — Hugging Face Model Bundler.
"""

import json
import logging
from pathlib import Path

from app.integrations.autoscientist.models import AutoScientistResult
from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig

logger = logging.getLogger("dataset_genome.publication.huggingface.model")


class ModelPublisher:
    """Prepares Hugging Face model repo files."""

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config

    def prepare(self, result: AutoScientistResult, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        config_data = {
            "architectures": ["AutoScientistForCausalLM"],
            "model_type": "autoscientist",
            "job_id": result.job_id,
        }
        (target_dir / "config.json").write_text(json.dumps(config_data, indent=2), encoding="utf-8")
        return target_dir

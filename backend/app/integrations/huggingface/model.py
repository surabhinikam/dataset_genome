"""
backend/app/integrations/huggingface/model.py — MODULE 2: Model Publisher.

Prepares trained model metadata, checkpoint weight paths, evaluation metrics,
and model card README.md documentation for Hugging Face Hub publication.
"""

import logging
import uuid
from typing import Dict, Optional

from app.integrations.huggingface.cards import ModelCardGenerator
from app.integrations.huggingface.config import DEFAULT_HF_CONFIG, HuggingFaceConfig
from app.integrations.huggingface.models import ModelArtifactPackage

logger = logging.getLogger("dataset_genome.integrations.huggingface.model")


class ModelPublisher:
    """
    MODULE 2 — Model Publisher.
    
    Bundles model checkpoints, architecture metadata, evaluation metrics,
    and attached README.md model cards.
    """

    def __init__(self, config: HuggingFaceConfig = DEFAULT_HF_CONFIG) -> None:
        self.config = config
        self.card_generator = ModelCardGenerator(config=config)

    def prepare_package(
        self,
        model_version: str = "v1.0",
        dataset_version: str = "v2.0-adaptive",
        architecture: str = "Transformer-AutoScientist-v1",
        checkpoint_path: str = "models/checkpoints/autoscientist_v1.pt",
        evaluation_metrics: Optional[Dict[str, float]] = None,
    ) -> ModelArtifactPackage:
        """
        Prepare a ModelArtifactPackage for publication.
        """
        logger.info(f"Module 2 (ModelPublisher) bundling model package for version '{model_version}'...")

        artifact_id = f"pkg-mdl-{uuid.uuid4().hex[:8]}"
        metrics = evaluation_metrics or {"accuracy": 0.88, "f1_macro": 0.86, "reasoning_quality": 88.5}

        card_text = self.card_generator.generate_card(
            model_version=model_version,
            dataset_version=dataset_version,
            architecture=architecture,
            metrics=metrics,
        )

        package = ModelArtifactPackage(
            model_id=artifact_id,
            model_version=model_version,
            architecture=architecture,
            checkpoint_path=checkpoint_path,
            evaluation_metrics=metrics,
            model_card_markdown=card_text,
        )

        logger.info(f"Module 2 (ModelPublisher) completed: ModelArtifactPackage '{artifact_id}' created successfully.")
        return package

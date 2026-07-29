"""
backend/app/integrations/shared/validators.py — Artifact Validation Module.

Pre-upload validator ensuring datasets, models, metadata, READMEs, and licenses pass validation before publication.
Rejects invalid publication attempts.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from app.integrations.shared.exceptions import ValidationError

logger = logging.getLogger("dataset_genome.integrations.shared.validators")


class ArtifactValidator:
    """
    Validates Dataset Genome release artifacts prior to Hugging Face or Kaggle upload.
    """

    def validate_dataset_file(self, dataset_path: Union[str, Path]) -> bool:
        """Validate dataset file existence, readability, and non-empty content."""
        path = Path(dataset_path)
        if not path.exists():
            raise ValidationError(f"Dataset file '{path}' does not exist.")
        if path.stat().st_size == 0:
            raise ValidationError(f"Dataset file '{path}' is empty (0 bytes).")
        logger.info(f"ArtifactValidator: Dataset file '{path.name}' passed validation ({path.stat().st_size} bytes).")
        return True

    def validate_model_checkpoint(self, checkpoint_path: Union[str, Path]) -> bool:
        """Validate model checkpoint path or manifest file."""
        path = Path(checkpoint_path)
        if not path.exists():
            raise ValidationError(f"Model checkpoint path '{path}' does not exist.")
        logger.info(f"ArtifactValidator: Model checkpoint '{path.name}' passed validation.")
        return True

    def validate_metadata_file(self, metadata_path: Union[str, Path]) -> bool:
        """Validate JSON metadata format."""
        path = Path(metadata_path)
        if not path.exists():
            raise ValidationError(f"Metadata file '{path}' does not exist.")
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValidationError(f"Metadata JSON in '{path}' must be a valid JSON object.")
        except Exception as exc:
            raise ValidationError(f"Failed to parse metadata JSON in '{path}': {exc}") from exc
        logger.info(f"ArtifactValidator: Metadata file '{path.name}' passed JSON validation.")
        return True

    def validate_readme_file(self, readme_path: Union[str, Path]) -> bool:
        """Validate README.md documentation card."""
        path = Path(readme_path)
        if not path.exists():
            raise ValidationError(f"README markdown file '{path}' does not exist.")
        content = path.read_text(encoding="utf-8")
        if len(content.strip()) < 20:
            raise ValidationError(f"README markdown file '{path}' is too short (< 20 chars).")
        logger.info(f"ArtifactValidator: README file '{path.name}' passed validation.")
        return True

    def validate_license_file(self, license_path: Union[str, Path]) -> bool:
        """Validate license file."""
        path = Path(license_path)
        if not path.exists():
            raise ValidationError(f"License file '{path}' does not exist.")
        logger.info(f"ArtifactValidator: License file '{path.name}' passed validation.")
        return True

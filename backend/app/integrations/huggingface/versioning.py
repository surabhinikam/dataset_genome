"""
backend/app/integrations/huggingface/versioning.py — MODULE 5: Version Manager.

Tracks dataset & model release lineage (Dataset v1, Dataset v2, Dataset v3),
recording release timestamps, change logs, adaptive scores, and training scores.
Generates DatasetVersionRecord history.
"""

import logging
from typing import List, Optional

from app.integrations.huggingface.models import DatasetVersionRecord

logger = logging.getLogger("dataset_genome.integrations.huggingface.versioning")


class VersionManager:
    """
    MODULE 5 — Version Manager.
    
    Manages semantic dataset versioning (v1.0 -> v2.0 -> v3.0) and maintains lineage changelogs.
    """

    def __init__(self) -> None:
        self._history: List[DatasetVersionRecord] = []

    def record_version(
        self,
        version_tag: str,
        changes: str,
        adaptive_score: float,
        training_score: float,
    ) -> DatasetVersionRecord:
        """
        Create and append a new DatasetVersionRecord entry.
        """
        logger.info(f"Module 5 (VersionManager) recording version '{version_tag}' (Adaptive: {adaptive_score}, Training: {training_score})...")

        record = DatasetVersionRecord(
            version_tag=version_tag,
            changes=changes,
            adaptive_score=adaptive_score,
            training_score=training_score,
        )
        self._history.append(record)
        return record

    def get_history(self) -> List[DatasetVersionRecord]:
        """
        Retrieve complete version lineage history.
        """
        return self._history

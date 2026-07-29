"""
backend/app/publication/versioning/model_version.py — Model Version Manager.

Tracks semantic model checkpoint versions (v1.0, v1.1, v2.0, etc.).
"""

import logging
from typing import List

logger = logging.getLogger("dataset_genome.publication.versioning.model")


class ModelVersionManager:
    """Manages semantic model release version tags."""

    def __init__(self) -> None:
        self._versions: List[str] = ["v1.0"]

    def current_version(self) -> str:
        return self._versions[-1]

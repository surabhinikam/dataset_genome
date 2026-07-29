"""
backend/app/publication/versioning/dataset_version.py — Dataset Version Manager.

Tracks semantic dataset versions (v1.0, v1.1, v2.0, etc.).
"""

import logging
from typing import List

logger = logging.getLogger("dataset_genome.publication.versioning.dataset")


class DatasetVersionManager:
    """Manages semantic dataset release version tags."""

    def __init__(self) -> None:
        self._versions: List[str] = ["v1.0", "v1.1", "v2.0"]

    def current_version(self) -> str:
        return self._versions[-1]

    def increment_major(self) -> str:
        current = self._versions[-1]
        major = int(current.lstrip("v").split(".")[0]) + 1
        new_v = f"v{major}.0"
        self._versions.append(new_v)
        return new_v

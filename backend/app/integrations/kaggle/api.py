"""
backend/app/integrations/kaggle/api.py — Kaggle API Wrapper.

Integrates official Kaggle API for dataset creation, dataset version update, metadata upload, and status checking.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from app.integrations.kaggle.auth import KaggleAuth
from app.integrations.shared.exceptions import UploadError

logger = logging.getLogger("dataset_genome.integrations.kaggle.api")


class KaggleApiWrapper:
    """
    Wrapper over official Kaggle API.
    """

    def __init__(self, username: Optional[str] = None, key: Optional[str] = None) -> None:
        self.auth = KaggleAuth(username=username, key=key)

    def dataset_exists(self, dataset_slug: str) -> bool:
        """Check if Kaggle dataset exists."""
        if not self.auth.authenticate():
            return False

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            res = api.dataset_list(search=dataset_slug)
            return len(res) > 0
        except Exception as exc:
            logger.warning(f"Error checking Kaggle dataset existence for '{dataset_slug}': {exc}")
            return False

    def create_dataset(self, folder_path: Union[str, Path], public: bool = True) -> str:
        """Create new dataset on Kaggle."""
        path = Path(folder_path)

        if not self.auth.authenticate():
            logger.info(f"Mock Mode: Simulating Kaggle dataset creation from '{path.name}'.")
            return f"https://www.kaggle.com/datasets/{self.auth.username or 'datasetgenome'}/{path.name}"

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            api.dataset_create_new(folder=str(path), dir_mode="zip", public=public)
            url = f"https://www.kaggle.com/datasets/{self.auth.username}/{path.name}"
            logger.info(f"Successfully created Kaggle dataset at '{url}'.")
            return url
        except Exception as exc:
            raise UploadError(f"Failed to create Kaggle dataset from '{path}': {exc}") from exc

    def update_dataset_version(
        self,
        folder_path: Union[str, Path],
        version_notes: str = "Dataset Genome evolutionary update",
    ) -> str:
        """Create new version of existing Kaggle dataset."""
        path = Path(folder_path)

        if not self.auth.authenticate():
            logger.info(f"Mock Mode: Simulating Kaggle version update for '{path.name}'.")
            return f"https://www.kaggle.com/datasets/{self.auth.username or 'datasetgenome'}/{path.name}"

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            api.dataset_create_version(folder=str(path), version_notes=version_notes, dir_mode="zip")
            url = f"https://www.kaggle.com/datasets/{self.auth.username}/{path.name}"
            logger.info(f"Successfully updated Kaggle dataset version at '{url}'.")
            return url
        except Exception as exc:
            raise UploadError(f"Failed to update Kaggle dataset version from '{path}': {exc}") from exc

"""
backend/app/integrations/kaggle/uploader.py — High-Level Production Kaggle Uploader.

Integrates KaggleApiWrapper and ArtifactValidator.
Produces structured logs with timestamp, repository, artifact, status, execution_time.
Includes network retry support for Kaggle release uploads.
"""

from datetime import datetime
import logging
from pathlib import Path
import time
from typing import Any, Dict, Optional, Union

from app.integrations.kaggle.api import KaggleApiWrapper
from app.integrations.shared.exceptions import UploadError
from app.integrations.shared.validators import ArtifactValidator

logger = logging.getLogger("dataset_genome.integrations.kaggle.uploader")


class ProductionKaggleUploader:
    """
    Production Uploader delegating to real Kaggle SDK with retry support.
    """

    def __init__(self, username: Optional[str] = None, key: Optional[str] = None, max_retries: int = 3) -> None:
        self.api = KaggleApiWrapper(username=username, key=key)
        self.validator = ArtifactValidator()
        self.max_retries = max_retries

    def upload_dataset(
        self,
        folder_path: Union[str, Path],
        dataset_slug: str = "dataset-genome-scientific-reasoning",
        public: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate, prepare metadata, and upload dataset folder to Kaggle.
        """
        start_t = time.time()
        path = Path(folder_path)

        # 1. Validation
        meta_file = path / "dataset-metadata.json"
        if meta_file.exists():
            self.validator.validate_metadata_file(meta_file)

        logger.info(f"ProductionKaggleUploader publishing dataset from '{path.name}' to Kaggle...")

        # 2. Upload with Retry
        attempt = 0
        last_exc = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                if self.api.dataset_exists(dataset_slug):
                    url = self.api.update_dataset_version(folder_path=path)
                else:
                    url = self.api.create_dataset(folder_path=path, public=public)

                elapsed = round(time.time() - start_t, 2)
                log_meta = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "repository": f"kaggle/{dataset_slug}",
                    "artifact": str(path.name),
                    "status": "SUCCESS",
                    "execution_time_seconds": elapsed,
                    "url": url,
                }
                logger.info(f"KAGGLE_UPLOAD_LOG: {log_meta}")
                return log_meta

            except Exception as exc:
                last_exc = exc
                logger.warning(f"Kaggle upload attempt {attempt}/{self.max_retries} failed for '{dataset_slug}': {exc}")
                time.sleep(0.2 * attempt)

        elapsed = round(time.time() - start_t, 2)
        log_meta = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": f"kaggle/{dataset_slug}",
            "artifact": str(path.name),
            "status": "FAILED",
            "execution_time_seconds": elapsed,
            "error": str(last_exc),
        }
        logger.error(f"KAGGLE_UPLOAD_LOG: {log_meta}")
        raise UploadError(f"Kaggle upload failed for '{dataset_slug}': {last_exc}") from last_exc

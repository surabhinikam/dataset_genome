"""
backend/app/integrations/huggingface/uploader.py — High-Level Production Hugging Face Uploader.

Integrates HuggingFaceHubWrapper, HuggingFaceDatasetsWrapper, and ArtifactValidator.
Produces structured upload logs: timestamp, repository, artifact, status, execution_time.
Includes network retry support for production publishing.
"""

from datetime import datetime
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

from app.integrations.huggingface.datasets import HuggingFaceDatasetsWrapper
from app.integrations.huggingface.hub import HuggingFaceHubWrapper
from app.integrations.shared.exceptions import UploadError, ValidationError
from app.integrations.shared.validators import ArtifactValidator

logger = logging.getLogger("dataset_genome.integrations.huggingface.uploader")


class ProductionHuggingFaceUploader:
    """
    Production Uploader delegating to real Hugging Face SDKs with retry support.
    """

    def __init__(self, token: Optional[str] = None, max_retries: int = 3) -> None:
        self.hub = HuggingFaceHubWrapper(token=token)
        self.datasets_sdk = HuggingFaceDatasetsWrapper()
        self.validator = ArtifactValidator()
        self.max_retries = max_retries

    def upload_dataset_repo(
        self,
        folder_path: Union[str, Path],
        repo_id: str,
        private: bool = False,
    ) -> Dict[str, Any]:
        """
        Validate, create repo, and upload dataset folder to Hugging Face Hub.
        """
        start_t = time.time()
        path = Path(folder_path)

        # 1. Validation
        readme_file = path / "README.md"
        if readme_file.exists():
            self.validator.validate_readme_file(readme_file)

        logger.info(f"ProductionHuggingFaceUploader publishing dataset '{path.name}' to '{repo_id}'...")

        # 2. Repo Creation & Upload with Retry
        attempt = 0
        last_exc = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                self.hub.create_repo(repo_id=repo_id, repo_type="dataset", private=private)
                url = self.hub.upload_folder(folder_path=path, repo_id=repo_id, repo_type="dataset")
                elapsed = round(time.time() - start_t, 2)

                log_meta = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "repository": repo_id,
                    "artifact": str(path.name),
                    "status": "SUCCESS",
                    "execution_time_seconds": elapsed,
                    "url": url,
                }
                logger.info(f"HUGGINGFACE_UPLOAD_LOG: {log_meta}")
                return log_meta

            except Exception as exc:
                last_exc = exc
                logger.warning(f"Upload attempt {attempt}/{self.max_retries} failed for '{repo_id}': {exc}")
                time.sleep(0.2 * attempt)

        elapsed = round(time.time() - start_t, 2)
        log_meta = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": repo_id,
            "artifact": str(path.name),
            "status": "FAILED",
            "execution_time_seconds": elapsed,
            "error": str(last_exc),
        }
        logger.error(f"HUGGINGFACE_UPLOAD_LOG: {log_meta}")
        raise UploadError(f"Hugging Face upload failed for '{repo_id}': {last_exc}") from last_exc

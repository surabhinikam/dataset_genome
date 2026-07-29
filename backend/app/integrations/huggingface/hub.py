"""
backend/app/integrations/huggingface/hub.py — Hugging Face Hub API Wrapper.

Integrates official huggingface_hub SDK for repo creation, existence checks, and artifact uploads.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from app.integrations.huggingface.auth import HuggingFaceAuth
from app.integrations.shared.exceptions import UploadError

logger = logging.getLogger("dataset_genome.integrations.huggingface.hub")


class HuggingFaceHubWrapper:
    """
    Wrapper over official huggingface_hub SDK.
    """

    def __init__(self, token: Optional[str] = None) -> None:
        self.auth = HuggingFaceAuth(token=token)
        self.token = self.auth.token

    def repo_exists(self, repo_id: str, repo_type: str = "dataset") -> bool:
        """Check if repository exists on Hugging Face Hub."""
        if not self.token:
            return False

        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            return api.repo_exists(repo_id=repo_id, repo_type=repo_type)
        except Exception as exc:
            logger.warning(f"Error checking repo existence for '{repo_id}': {exc}")
            return False

    def create_repo(self, repo_id: str, repo_type: str = "dataset", private: bool = False) -> str:
        """Create repository on Hugging Face Hub."""
        if not self.token:
            logger.info(f"Mock Mode: Simulating repo creation for '{repo_id}' ({repo_type}).")
            return f"https://huggingface.co/{repo_type}s/{repo_id}"

        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            url = api.create_repo(repo_id=repo_id, repo_type=repo_type, private=private, exist_ok=True)
            logger.info(f"Successfully created Hugging Face repo '{repo_id}' ({url}).")
            return str(url)
        except Exception as exc:
            raise UploadError(f"Failed to create Hugging Face repo '{repo_id}': {exc}") from exc

    def upload_file(
        self,
        path_or_fileobj: Union[str, Path],
        path_in_repo: str,
        repo_id: str,
        repo_type: str = "dataset",
    ) -> str:
        """Upload single file to Hugging Face Hub."""
        if not self.token:
            logger.info(f"Mock Mode: Simulating upload of file '{path_in_repo}' to '{repo_id}'.")
            return f"https://huggingface.co/{repo_type}s/{repo_id}/raw/main/{path_in_repo}"

        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            res = api.upload_file(
                path_or_fileobj=str(path_or_fileobj),
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type=repo_type,
            )
            logger.info(f"Uploaded file '{path_in_repo}' to '{repo_id}'.")
            return str(res)
        except Exception as exc:
            raise UploadError(f"Failed to upload file '{path_in_repo}' to '{repo_id}': {exc}") from exc

    def upload_folder(
        self,
        folder_path: Union[str, Path],
        repo_id: str,
        repo_type: str = "dataset",
    ) -> str:
        """Upload entire folder directory to Hugging Face Hub."""
        if not self.token:
            logger.info(f"Mock Mode: Simulating folder upload from '{folder_path}' to '{repo_id}'.")
            return f"https://huggingface.co/{repo_type}s/{repo_id}"

        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            res = api.upload_folder(
                folder_path=str(folder_path),
                repo_id=repo_id,
                repo_type=repo_type,
            )
            logger.info(f"Uploaded folder '{folder_path}' to '{repo_id}'.")
            return str(res)
        except Exception as exc:
            raise UploadError(f"Failed to upload folder '{folder_path}' to '{repo_id}': {exc}") from exc

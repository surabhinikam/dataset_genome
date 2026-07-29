"""
backend/app/integrations/huggingface/downloader.py — Hugging Face Downloader Utilities.

Provides hf_hub_download and snapshot_download abstractions for fetching datasets and models.
"""

import logging
from pathlib import Path
from typing import Optional, Union

from app.integrations.huggingface.auth import HuggingFaceAuth

logger = logging.getLogger("dataset_genome.integrations.huggingface.downloader")


class HuggingFaceDownloader:
    """Download manager for Hugging Face Hub repos."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.auth = HuggingFaceAuth(token=token)
        self.token = self.auth.token

    def download_file(self, repo_id: str, filename: str, repo_type: str = "dataset") -> Optional[str]:
        """Download a single file from Hub repo."""
        if not self.token:
            logger.info(f"Mock Mode: Simulating file download of '{filename}' from '{repo_id}'.")
            return f"mock/downloads/{repo_id}/{filename}"

        try:
            from huggingface_hub import hf_hub_download
            res = hf_hub_download(repo_id=repo_id, filename=filename, repo_type=repo_type, token=self.token)
            logger.info(f"Successfully downloaded '{filename}' from '{repo_id}' to '{res}'.")
            return str(res)
        except Exception as exc:
            logger.warning(f"Failed to download '{filename}' from '{repo_id}': {exc}")
            return None

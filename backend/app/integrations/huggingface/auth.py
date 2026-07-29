"""
backend/app/integrations/huggingface/auth.py — Hugging Face Authentication Helper.

Handles login with HF_TOKEN and token verification.
"""

import logging
from typing import Optional
from app.integrations.shared.credentials import get_credentials
from app.integrations.shared.exceptions import IntegrationAuthError

logger = logging.getLogger("dataset_genome.integrations.huggingface.auth")


class HuggingFaceAuth:
    """Manages Hugging Face Hub access token authentication."""

    def __init__(self, token: Optional[str] = None) -> None:
        creds = get_credentials()
        self.token = token or creds.hf_token

    def authenticate(self) -> bool:
        """Authenticate using huggingface_hub API if token present."""
        if not self.token:
            logger.info("No HF_TOKEN provided. Operating in unauthenticated / mock mode.")
            return False

        try:
            from huggingface_hub import HfApi
            api = HfApi(token=self.token)
            user_info = api.whoami()
            logger.info(f"Hugging Face Authentication Successful! Authenticated as: '{user_info.get('name')}'")
            return True
        except Exception as exc:
            logger.warning(f"Hugging Face Authentication check failed: {exc}")
            return False

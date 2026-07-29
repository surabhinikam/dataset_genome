"""
backend/app/integrations/kaggle/auth.py — Kaggle API Authentication.

Authenticates Kaggle API using environment variables (KAGGLE_USERNAME, KAGGLE_KEY).
"""

import logging
import os
from typing import Optional
from app.integrations.shared.credentials import get_credentials

logger = logging.getLogger("dataset_genome.integrations.kaggle.auth")


class KaggleAuth:
    """Manages Kaggle API authentication."""

    def __init__(self, username: Optional[str] = None, key: Optional[str] = None) -> None:
        creds = get_credentials()
        self.username = username or creds.kaggle_username
        self.key = key or creds.kaggle_key

    def authenticate(self) -> bool:
        """Authenticate using official kaggle API if credentials present."""
        if not self.username or not self.key:
            logger.info("No Kaggle credentials provided. Operating in unauthenticated / mock mode.")
            return False

        os.environ["KAGGLE_USERNAME"] = self.username
        os.environ["KAGGLE_KEY"] = self.key

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            logger.info(f"Kaggle Authentication Successful! Authenticated as: '{self.username}'")
            return True
        except Exception as exc:
            logger.warning(f"Kaggle Authentication check failed: {exc}")
            return False

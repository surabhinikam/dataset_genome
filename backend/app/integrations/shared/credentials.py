"""
backend/app/integrations/shared/credentials.py — Ecosystem Credentials Loader.

Loads credentials safely from environment variables (HF_TOKEN, KAGGLE_USERNAME, KAGGLE_KEY).
Never hardcodes tokens.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class IntegrationCredentials(BaseModel):
    """Holds open-source ecosystem credentials."""
    hf_token: Optional[str] = Field(None, description="Hugging Face User Access Token (HF_TOKEN)")
    kaggle_username: Optional[str] = Field(None, description="Kaggle API Username (KAGGLE_USERNAME)")
    kaggle_key: Optional[str] = Field(None, description="Kaggle API Key (KAGGLE_KEY)")

    @property
    def has_hf_token(self) -> bool:
        return bool(self.hf_token and self.hf_token.strip())

    @property
    def has_kaggle_creds(self) -> bool:
        return bool(self.kaggle_username and self.kaggle_key)


def get_credentials() -> IntegrationCredentials:
    """Load ecosystem credentials from process environment variables."""
    return IntegrationCredentials(
        hf_token=os.getenv("HF_TOKEN"),
        kaggle_username=os.getenv("KAGGLE_USERNAME"),
        kaggle_key=os.getenv("KAGGLE_KEY"),
    )

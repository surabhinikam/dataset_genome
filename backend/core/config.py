"""
core/config.py — Application-wide configuration using pydantic-settings.

All environment-sensitive values are centralised here so that changing
behaviour across environments requires editing only this file (or env vars).
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --------------- App metadata ---------------
    app_name: str = "Dataset Genome API"
    app_version: str = "0.1.0"
    debug: bool = False

    # --------------- CORS ---------------
    # Comma-separated origins; defaults to local Next.js dev server
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # --------------- File storage ---------------
    # Directory where uploaded CSV files are persisted
    upload_dir: Path = Path(__file__).resolve().parent.parent / "uploads"

    # Maximum allowed upload size in bytes (50 MB)
    max_upload_size_bytes: int = 50 * 1024 * 1024

    # Allowed MIME types for uploaded files
    allowed_content_types: list[str] = [
        "text/csv",
        "application/csv",
        "application/vnd.ms-excel",
        "text/plain",
    ]

    # Allowed file extensions (lower-cased)
    allowed_extensions: list[str] = [".csv"]


# Module-level singleton — import this everywhere instead of instantiating
# Settings repeatedly.
settings = Settings()

# Ensure the upload directory exists at startup
settings.upload_dir.mkdir(parents=True, exist_ok=True)

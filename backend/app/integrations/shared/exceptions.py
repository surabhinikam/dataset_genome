"""
backend/app/integrations/shared/exceptions.py — Integration Custom Exception Hierarchy.
"""


class DatasetGenomeIntegrationError(Exception):
    """Base exception for all Dataset Genome ecosystem integration errors."""
    pass


class IntegrationAuthError(DatasetGenomeIntegrationError):
    """Raised when authentication fails or required environment token is missing."""
    pass


class UploadError(DatasetGenomeIntegrationError):
    """Raised when artifact upload to Hugging Face or Kaggle fails."""
    pass


class ValidationError(DatasetGenomeIntegrationError):
    """Raised when pre-upload artifact validation fails."""
    pass


class NetworkError(DatasetGenomeIntegrationError):
    """Raised when network retries fail or timeout occurs."""
    pass

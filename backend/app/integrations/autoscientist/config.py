"""
backend/app/integrations/autoscientist/config.py — AutoScientist Integration Config.

Defines configuration parameters, target thresholds, and client timeout settings.
"""

from pydantic import BaseModel, Field


class AutoScientistConfig(BaseModel):
    """Configuration settings for AutoScientist Integration Layer."""

    target_api_url: str = Field("http://localhost:8000/autoscientist", description="Base URL of AutoScientist service")
    client_timeout_seconds: int = Field(30, description="HTTP client request timeout in seconds")
    batch_submission_size: int = Field(50, description="Max batch size per submission request")
    enable_mock_client: bool = Field(True, description="Use MockAutoScientistClient for offline execution & testing")

    # Evaluation & Feedback thresholds
    weakness_accuracy_threshold: float = Field(0.70, ge=0.0, le=1.0, description="Accuracy threshold below which a domain is marked weak")
    target_confidence_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Target minimum model confidence threshold")


DEFAULT_AUTOSCIENTIST_CONFIG = AutoScientistConfig()

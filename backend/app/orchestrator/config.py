"""
backend/app/orchestrator/config.py — Orchestrator Engine Configuration.

Defines default execution parameters, retries, and output directory settings.
"""

from pydantic import BaseModel, Field


class OrchestratorConfig(BaseModel):
    """Configuration settings for Dataset Genome Orchestrator Engine."""

    default_domain: str = Field("Agriculture", description="Default domain for dataset generation")
    default_sample_count: int = Field(20, description="Default sample count per dataset run")
    max_stage_retries: int = Field(2, ge=0, description="Maximum retries per pipeline stage upon failure")
    enable_events: bool = Field(True, description="Enable event broadcasting to listeners")
    output_report_dir: str = Field("publication/reports", description="Path to write run_report.json and run_report.md")


DEFAULT_ORCHESTRATOR_CONFIG = OrchestratorConfig()

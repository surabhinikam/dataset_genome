"""
schemas/dataset.py — Pydantic models for dataset-related API responses.

These models define the contract between the backend and frontend. Any change
here should be mirrored in the TypeScript types on the frontend.
"""

from uuid import UUID
from pydantic import BaseModel, Field


class DatasetMetadataResponse(BaseModel):
    """
    Response model returned after a successful CSV upload and analysis.

    Attributes
    ----------
    dataset_id : UUID
        Unique identifier generated for this upload session.
    filename : str
        Original filename as provided by the client.
    num_rows : int
        Total number of data rows (excluding the header).
    num_cols : int
        Total number of columns in the CSV.
    column_names : list[str]
        Ordered list of column header names.
    """

    dataset_id: UUID = Field(..., description="Unique identifier for the upload")
    filename: str = Field(..., description="Original CSV filename")
    num_rows: int = Field(..., ge=0, description="Number of data rows")
    num_cols: int = Field(..., ge=0, description="Number of columns")
    column_names: list[str] = Field(..., description="Ordered list of column headers")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "filename": "iris.csv",
                "num_rows": 150,
                "num_cols": 5,
                "column_names": [
                    "sepal_length",
                    "sepal_width",
                    "petal_length",
                    "petal_width",
                    "species",
                ],
            }
        }
    }


class HealthResponse(BaseModel):
    """Response model for the health-check endpoint."""

    status: str = Field(..., description="Service status ('ok' when healthy)")
    version: str = Field(..., description="API version string")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "version": "0.1.0"
            }
        }
    }


class AnalyzeDatasetRequest(BaseModel):
    """Request model for POST /analyze endpoint."""

    dataset_id: UUID = Field(..., description="UUID of the dataset to analyze")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }
    }


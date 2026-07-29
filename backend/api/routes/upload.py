"""
api/routes/upload.py — CSV upload endpoint.

Responsibilities (in order):
  1. Validate the uploaded file (extension + MIME type).
  2. Save it to the configured uploads directory.
  3. Process the CSV to extract structural metadata.
  4. Return the metadata as a JSON response.

Error handling follows HTTP semantics — bad input → 4xx, server fault → 5xx.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.dataset import DatasetMetadataResponse
from services.csv_processor import process_csv
from utils.file_utils import generate_upload_path, save_upload_file, validate_csv_file

router = APIRouter(tags=["upload"])


@router.post(
    "/upload",
    response_model=DatasetMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload CSV Dataset",
    description=(
        "Accepts a CSV file, validates it, persists it to the uploads directory, "
        "and returns structural metadata (row count, column count, column names)."
    ),
)
async def upload_csv(
    file: UploadFile = File(..., description="A valid CSV file to analyse"),
) -> DatasetMetadataResponse:
    """
    POST /upload — validate, save, and analyse a CSV file.

    Returns
    -------
    DatasetMetadataResponse
        Metadata extracted from the uploaded CSV.
    """
    # Guard: ensure a filename is present
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename was provided with the upload.",
        )

    # Step 1 — validate file type
    validate_csv_file(file)

    # Step 2 — generate a unique path and save the file
    dataset_id, file_path = generate_upload_path(file.filename)
    await save_upload_file(file, file_path)

    # Step 3 — extract CSV metadata via the service layer
    metadata = process_csv(
        file_path=file_path,
        dataset_id=dataset_id,
        original_filename=file.filename,
    )

    # Step 4 — return the validated response model
    return DatasetMetadataResponse(**metadata)

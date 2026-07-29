"""
utils/file_utils.py — File validation and path generation utilities.

Keeping validation logic here (rather than inside route handlers) makes it
easy to reuse across multiple endpoints and to test in isolation.
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from core.config import settings


def validate_csv_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is an acceptable CSV.

    Raises
    ------
    HTTPException (400)
        If the file extension or MIME type is not allowed.
    HTTPException (413)
        If the file size exceeds the configured limit (checked after read).
    """
    # --- Extension check ---
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file extension '{suffix}'. "
                f"Only {settings.allowed_extensions} files are accepted."
            ),
        )

    # --- MIME-type check ---
    # content_type may include encoding hints (e.g. "text/csv; charset=utf-8"),
    # so we strip everything after the first semicolon.
    raw_content_type = (file.content_type or "").split(";")[0].strip()
    if raw_content_type and raw_content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid content type '{raw_content_type}'. "
                f"Allowed types: {settings.allowed_content_types}."
            ),
        )


def generate_upload_path(original_filename: str) -> tuple[uuid.UUID, Path]:
    """
    Create a unique upload path for the given original filename.

    Returns
    -------
    (dataset_id, file_path)
        dataset_id — freshly generated UUID for this upload session.
        file_path  — absolute Path where the file should be saved.
    """
    dataset_id = uuid.uuid4()
    # Prefix the filename with the UUID to prevent collisions
    safe_name = f"{dataset_id}_{Path(original_filename).name}"
    file_path = settings.upload_dir / safe_name
    return dataset_id, file_path


async def save_upload_file(upload_file: UploadFile, destination: Path) -> int:
    """
    Stream the uploaded file to *destination* and return the total byte count.

    Raises
    ------
    HTTPException (413)
        If the file exceeds the configured size limit.
    """
    total_bytes = 0
    chunk_size = 1024 * 64  # 64 KB chunks

    with destination.open("wb") as out_file:
        while chunk := await upload_file.read(chunk_size):
            total_bytes += len(chunk)
            if total_bytes > settings.max_upload_size_bytes:
                # Clean up the partial file before raising
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=(
                        f"File exceeds the maximum allowed size of "
                        f"{settings.max_upload_size_bytes // (1024 * 1024)} MB."
                    ),
                )
            out_file.write(chunk)

    return total_bytes


def find_file_by_dataset_id(dataset_id: str | uuid.UUID) -> tuple[Path, str]:
    """
    Search settings.upload_dir for a file matching the given dataset_id prefix.

    Returns
    -------
    tuple[Path, str]
        (file_path, original_filename)

    Raises
    ------
    HTTPException (404)
        If no matching file is found.
    """
    dataset_str = str(dataset_id).lower()
    for file in settings.upload_dir.glob("*"):
        if file.is_file() and file.name.lower().startswith(dataset_str):
            # Filename format is {uuid}_{original_filename}
            parts = file.name.split("_", 1)
            original_name = parts[1] if len(parts) > 1 else file.name
            return file, original_name

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Dataset with ID '{dataset_id}' was not found in uploads.",
    )

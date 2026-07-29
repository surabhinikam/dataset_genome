"""
services/csv_processor.py — Business-logic layer for CSV analysis.

This service is intentionally decoupled from FastAPI so it can be called
from tests, background tasks, or CLI scripts without an HTTP context.
"""

import uuid
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, status


def process_csv(file_path: Path, dataset_id: uuid.UUID, original_filename: str) -> dict:
    """
    Read a CSV file from disk and return its structural metadata.

    Parameters
    ----------
    file_path : Path
        Absolute path to the saved CSV file.
    dataset_id : uuid.UUID
        The UUID assigned to this upload session.
    original_filename : str
        The filename as provided by the client (used in the response).

    Returns
    -------
    dict
        Keys: dataset_id, filename, num_rows, num_cols, column_names.

    Raises
    ------
    HTTPException (422)
        If pandas cannot parse the file as a valid CSV.
    """
    try:
        # Read only the first row to retrieve column names efficiently,
        # then count rows without loading the entire frame into memory.
        df_header = pd.read_csv(file_path, nrows=0)
        column_names: list[str] = df_header.columns.tolist()

        # Count data rows by iterating in chunks — memory-efficient for large files.
        num_rows = sum(
            len(chunk)
            for chunk in pd.read_csv(file_path, chunksize=10_000, low_memory=False)
        )
        num_cols = len(column_names)

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded CSV file is empty.",
        )
    except pd.errors.ParserError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse CSV file: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while processing file: {exc}",
        )

    return {
        "dataset_id": dataset_id,
        "filename": original_filename,
        "num_rows": num_rows,
        "num_cols": num_cols,
        "column_names": column_names,
    }

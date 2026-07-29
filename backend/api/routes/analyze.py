"""
api/routes/analyze.py — Dataset Genome Analysis Endpoint (POST /analyze).

Executes Dataset Intelligence Engine on an uploaded dataset file and returns
the complete Genome Report JSON.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Body, Path, Query
from fastapi.concurrency import run_in_threadpool

from schemas.dataset import AnalyzeDatasetRequest
from schemas.intelligence import GenomeReportResponse
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(tags=["analyze"])
engine = DatasetIntelligenceEngine()


@router.post(
    "/analyze",
    response_model=GenomeReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Dataset Genome",
    description="Loads uploaded CSV by dataset_id, runs all 6 profilers, computes Health Score, and returns Genome Report.",
)
async def analyze_dataset(
    payload: Optional[AnalyzeDatasetRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> GenomeReportResponse:
    """
    POST /analyze — Accepts dataset_id via JSON body or query param.
    """
    target_id = payload.dataset_id if payload else dataset_id_query

    if not target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id in request body or query parameter.",
        )

    file_path, filename = find_file_by_dataset_id(target_id)

    # Run CPU-bound analysis off the main event loop threadpool
    report = await run_in_threadpool(
        engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=filename
    )

    return report


@router.post(
    "/analyze/{dataset_id}",
    response_model=GenomeReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Dataset Genome by Path Param",
    description="Loads uploaded CSV by dataset_id path parameter and returns Genome Report.",
)
async def analyze_dataset_by_path(
    dataset_id: UUID = Path(..., description="UUID of the dataset"),
) -> GenomeReportResponse:
    """
    POST /analyze/{dataset_id} — Accepts dataset_id in URL path.
    """
    file_path, filename = find_file_by_dataset_id(dataset_id)

    report = await run_in_threadpool(
        engine.analyze_file, file_path=file_path, dataset_id=dataset_id, filename=filename
    )

    return report

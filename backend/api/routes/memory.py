"""
api/routes/memory.py — Scientific Memory Engine API Endpoints.

Provides REST API routes for storing evaluation reports, searching historical experiments,
and retrieving memory records by ID.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status

from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.memory_engine import ScientificMemoryEngine
from services.autoscientist.memory_models import (
    MemoryRecord,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryStoreRequest,
    MemoryStoreResponse,
)

router = APIRouter(prefix="/autoscientist/memory", tags=["autoscientist-memory"])
memory_engine = ScientificMemoryEngine()


@router.post(
    "/store",
    response_model=MemoryStoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Store Evaluation Experiment in Memory",
    description="Encodes an EvaluationReport into a canonical MemoryRecord and persists it in the Scientific Memory Engine.",
)
async def store_memory_record(
    payload: Optional[MemoryStoreRequest] = Body(None),
) -> MemoryStoreResponse:
    """
    POST /autoscientist/memory/store — Accepts EvaluationReport object in JSON body.
    """
    if not payload or not payload.evaluation_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide an evaluation_report payload to store in memory.",
        )

    try:
        record = memory_engine.store_evaluation_report(
            report=payload.evaluation_report,
            dataset_id=payload.dataset_id,
        )
        return MemoryStoreResponse(
            record_id=record.record_id,
            experiment_id=record.experiment_id,
            memory_record=record,
            stored_at=record.stored_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/search",
    response_model=MemorySearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Similar Historical Experiments",
    description="Searches historical experiments using vector similarity metrics and returns ranked similar MemoryRecords.",
)
async def search_memory_records(
    payload: Optional[MemorySearchRequest] = Body(None),
) -> MemorySearchResponse:
    """
    POST /autoscientist/memory/search — Accepts category, top_k, metric, or query_vector search filters.
    """
    request = payload or MemorySearchRequest()

    try:
        retrieval_result = memory_engine.search_similar_experiments(request)
        return MemorySearchResponse(
            total_matches=len(retrieval_result.similar_records),
            retrieval_result=retrieval_result,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{id}",
    response_model=MemoryRecord,
    status_code=status.HTTP_200_OK,
    summary="Get Memory Record by ID",
    description="Retrieves a single MemoryRecord object by its record_id.",
)
async def get_memory_record_by_id(id: str) -> MemoryRecord:
    """
    GET /autoscientist/memory/{id} — Returns MemoryRecord matching record_id or 404.
    """
    record = memory_engine.get_memory_record(id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MemoryRecord with ID '{id}' was not found.",
        )
    return record

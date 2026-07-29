"""
api/routes/observe.py — AutoScientist Observation API Endpoint (POST /autoscientist/observe).

Converts a dataset Genome Report into structured ScientificObservation domain models.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.observation_models import ObservationRequest, ObservationResponse
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(prefix="/autoscientist", tags=["autoscientist"])
analysis_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()


@router.post(
    "/observe",
    response_model=ObservationResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Scientific Observations",
    description=(
        "Converts a dataset GenomeReportResponse into structured ScientificObservation models "
        "containing empirical evidence payloads and calibrated severity ratings."
    ),
)
async def extract_observations(
    payload: Optional[ObservationRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> ObservationResponse:
    """
    POST /autoscientist/observe — Accepts dataset_id or raw report in JSON body.
    """
    report: Optional[GenomeReportResponse] = None

    if payload and payload.report:
        report = payload.report
    else:
        target_id = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query

        if not target_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide dataset_id or raw report in request body or query parameter.",
            )

        file_path, filename = find_file_by_dataset_id(target_id)
        report = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=filename
        )

    observations = observation_engine.process_report(report)

    return ObservationResponse(
        dataset_id=report.dataset_id,
        filename=report.filename,
        total_observations=len(observations),
        overall_health_score=report.health_score.overall_score,
        observations=observations,
    )

"""
api/routes/rank.py — Problem Ranking Engine Endpoint (POST /autoscientist/rank).

Prioritizes extracted ScientificObservation objects into a deterministic PrioritizedProblemQueue.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.ranking_models import RankRequest, RankResponse
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(prefix="/autoscientist", tags=["autoscientist"])
analysis_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()
ranking_engine = ProblemRankingEngine()


@router.post(
    "/rank",
    response_model=RankResponse,
    status_code=status.HTTP_200_OK,
    summary="Rank Dataset Problems",
    description=(
        "Prioritizes scientific dataset observations into a deterministic PrioritizedProblemQueue "
        "using multi-criteria utility scoring (Severity, Info Loss Risk, Impact Potential, Repair Complexity)."
    ),
)
async def rank_dataset_problems(
    payload: Optional[RankRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> RankResponse:
    """
    POST /autoscientist/rank — Accepts dataset_id, raw observations, or GenomeReportResponse.
    """
    observations: List[ScientificObservation] = []
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query

    # 1. Observations provided directly in payload
    if payload and payload.observations is not None:
        observations = payload.observations

    # 2. GenomeReportResponse provided directly in payload
    elif payload and payload.report is not None:
        report = payload.report
        target_id = report.dataset_id
        observations = observation_engine.process_report(report)

    # 3. Analyze by dataset_id
    elif target_id is not None:
        file_path, filename = find_file_by_dataset_id(target_id)
        report: GenomeReportResponse = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=filename
        )
        observations = observation_engine.process_report(report)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, observations list, or report payload.",
        )

    # Execute deterministic problem ranking
    queue = ranking_engine.rank_observations(observations, dataset_id=target_id)

    return RankResponse(
        dataset_id=target_id,
        total_problems=queue.total_problems,
        queue=queue,
        ranked_problems=queue.ranked_problems,
    )

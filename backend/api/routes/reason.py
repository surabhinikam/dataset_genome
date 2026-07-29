"""
api/routes/reason.py — Reasoning Engine Endpoint (POST /autoscientist/reason).

Converts a prioritized problem into a structured Causal Reasoning Trace (ReasoningTrace).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.reasoning_models import ReasonRequest, ReasonResponse, ScientificMemoryInterface
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(prefix="/autoscientist", tags=["autoscientist"])
analysis_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()


@router.post(
    "/reason",
    response_model=ReasonResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Causal Reasoning Trace",
    description=(
        "Converts a PrioritizedProblem into a structured Causal Reasoning Trace (ReasoningTrace) "
        "inferring flaw mechanisms, supporting evidence, assumptions, constraints, risks, and recommended transformation class."
    ),
)
async def generate_reasoning(
    payload: Optional[ReasonRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> ReasonResponse:
    """
    POST /autoscientist/reason — Accepts ranked_problem, dataset_id, or GenomeReportResponse.
    """
    target_problem: Optional[RankedProblem] = None
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query
    filename = "dataset.csv"
    health_score = 100.0
    memory_stub = payload.memory_stub if (payload and payload.memory_stub) else ScientificMemoryInterface()

    # 1. Ranked problem provided directly in payload
    if payload and (payload.ranked_problem or payload.prioritized_problem):
        target_problem = payload.ranked_problem or payload.prioritized_problem

    # 2. GenomeReportResponse provided directly in payload
    elif payload and payload.report is not None:
        report = payload.report
        target_id = report.dataset_id
        filename = report.filename
        health_score = report.health_score.overall_score
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to reason about (0 observations extracted).",
            )
        target_problem = queue.highest_priority_problem

    # 3. Analyze by dataset_id
    elif target_id is not None:
        file_path, filename = find_file_by_dataset_id(target_id)
        report: GenomeReportResponse = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=filename
        )
        health_score = report.health_score.overall_score
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to reason about (0 observations extracted).",
            )
        target_problem = queue.highest_priority_problem

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, ranked_problem payload, or report payload.",
        )

    # Build ReasoningContext
    context = ReasoningContext(
        dataset_id=target_id,
        filename=filename,
        prioritized_problem=target_problem,
        health_score=health_score,
        memory_interface=memory_stub,
    )

    # Generate ReasoningTrace
    trace = reasoning_engine.generate_reasoning_trace(context)

    return ReasonResponse(
        dataset_id=target_id,
        problem_id=target_problem.observation_id,
        reasoning_trace=trace,
    )

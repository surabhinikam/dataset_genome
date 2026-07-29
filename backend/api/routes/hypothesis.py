"""
api/routes/hypothesis.py — Hypothesis Generator Endpoint (POST /autoscientist/hypothesis).

Converts a Causal ReasoningTrace into a testable, measurable, and falsifiable ScientificHypothesis.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import HypothesisRequest, HypothesisResponse, ScientificHypothesis
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.reasoning_models import ReasoningTrace
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(prefix="/autoscientist", tags=["autoscientist"])
analysis_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()
hypothesis_generator = ScientificHypothesisGenerator()


@router.post(
    "/hypothesis",
    response_model=HypothesisResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Scientific Hypothesis",
    description=(
        "Converts a Causal ReasoningTrace into a structured, testable, measurable, and falsifiable ScientificHypothesis "
        "specifying proposed transformation, parameters, predicted metric improvement delta, and risk level."
    ),
)
async def generate_scientific_hypothesis(
    payload: Optional[HypothesisRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> HypothesisResponse:
    """
    POST /autoscientist/hypothesis — Accepts reasoning_trace, dataset_id, or report.
    """
    target_trace: Optional[ReasoningTrace] = None
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query

    # 1. Reasoning trace provided directly in payload
    if payload and payload.reasoning_trace is not None:
        target_trace = payload.reasoning_trace

    # 2. GenomeReportResponse provided directly in payload
    elif payload and payload.report is not None:
        report = payload.report
        target_id = report.dataset_id
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to form hypotheses for (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=report.filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        target_trace = reasoning_engine.generate_reasoning_trace(context)

    # 3. Analyze by dataset_id
    elif target_id is not None:
        file_path, filename = find_file_by_dataset_id(target_id)
        report: GenomeReportResponse = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=filename
        )
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to form hypotheses for (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        target_trace = reasoning_engine.generate_reasoning_trace(context)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, reasoning_trace payload, or report payload.",
        )

    # Generate ScientificHypothesis
    hypothesis = hypothesis_generator.generate_hypothesis(target_trace)

    return HypothesisResponse(
        dataset_id=target_id,
        problem_id=target_trace.problem_id,
        hypothesis=hypothesis,
    )

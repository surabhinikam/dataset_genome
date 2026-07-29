"""
api/routes/plan.py — Experiment Planner Endpoint (POST /autoscientist/plan).

Converts a ScientificHypothesis into a validated, declarative ExperimentPlan.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.experiment_models import ExperimentPlan, PlanRequest, PlanResponse
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import ScientificHypothesis
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
experiment_planner = ExperimentPlanner()


@router.post(
    "/plan",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Experiment Plan",
    description=(
        "Converts a ScientificHypothesis into a validated, declarative ExperimentPlan "
        "containing execution steps, validation checklists, rollback procedures, and resource estimates."
    ),
)
async def generate_experiment_plan(
    payload: Optional[PlanRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> PlanResponse:
    """
    POST /autoscientist/plan — Accepts hypothesis, reasoning_trace, dataset_id, or report.
    """
    target_hypothesis: Optional[ScientificHypothesis] = None
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query

    # 1. Direct hypothesis provided in payload
    if payload and payload.hypothesis is not None:
        target_hypothesis = payload.hypothesis

    # 2. Reasoning trace provided in payload
    elif payload and payload.reasoning_trace is not None:
        target_hypothesis = hypothesis_generator.generate_hypothesis(payload.reasoning_trace)

    # 3. GenomeReportResponse provided directly in payload
    elif payload and payload.report is not None:
        report = payload.report
        target_id = report.dataset_id
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to plan experiments for (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=report.filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        trace = reasoning_engine.generate_reasoning_trace(context)
        target_hypothesis = hypothesis_generator.generate_hypothesis(trace)

    # 4. Analyze by dataset_id
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
                detail="Dataset has no problems to plan experiments for (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        trace = reasoning_engine.generate_reasoning_trace(context)
        target_hypothesis = hypothesis_generator.generate_hypothesis(trace)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, hypothesis, reasoning_trace, or report payload.",
        )

    # Generate ExperimentPlan
    plan = experiment_planner.create_plan(target_hypothesis)

    return PlanResponse(
        dataset_id=target_id,
        hypothesis_id=target_hypothesis.id,
        experiment_plan=plan,
    )

"""
api/routes/execute.py — Execution Engine Endpoint (POST /autoscientist/execute).

Executes approved ExperimentPlan objects in a sandboxed runner, manages versioning,
and produces ExecutionResult objects.
"""

from typing import Optional
from uuid import UUID
import pandas as pd
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.execution_engine import ExecutionEngine
from services.autoscientist.execution_models import ExecuteRequest, ExecuteResponse, ExecutionResult
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

router = APIRouter(prefix="/autoscientist", tags=["autoscientist"])
analysis_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()
hypothesis_generator = ScientificHypothesisGenerator()
experiment_planner = ExperimentPlanner()
execution_engine = ExecutionEngine()


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Experiment Plan",
    description=(
        "Executes an approved ExperimentPlan on a target dataset within an isolated sandbox, "
        "saving the mutated dataset to a new versioned lineage path and returning an ExecutionResult."
    ),
)
async def execute_experiment_plan(
    payload: Optional[ExecuteRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> ExecuteResponse:
    """
    POST /autoscientist/execute — Accepts experiment_plan, hypothesis, dataset_id, or report.
    """
    target_plan: Optional[ExperimentPlan] = None
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query
    target_df: Optional[pd.DataFrame] = None
    source_filename = "dataset.csv"

    # 1. Direct experiment_plan provided in payload
    if payload and payload.experiment_plan is not None:
        target_plan = payload.experiment_plan
        if target_id:
            file_path, source_filename = find_file_by_dataset_id(target_id)
            target_df = pd.read_csv(file_path, low_memory=False)
        else:
            # Generate sample dataframe if none provided
            target_df = pd.DataFrame({
                "facility_code": [999] * 15,
                "patient_id": [f"ID_{i}" for i in range(15)],
                "age": [20 + i for i in range(15)]
            })

    # 2. Hypothesis provided in payload
    elif payload and payload.hypothesis is not None:
        target_plan = experiment_planner.create_plan(payload.hypothesis)
        if target_id:
            file_path, source_filename = find_file_by_dataset_id(target_id)
            target_df = pd.read_csv(file_path, low_memory=False)
        else:
            target_df = pd.DataFrame({
                "facility_code": [999] * 15,
                "patient_id": [f"ID_{i}" for i in range(15)],
                "age": [20 + i for i in range(15)]
            })

    # 3. GenomeReportResponse provided directly in payload
    elif payload and payload.report is not None:
        report = payload.report
        target_id = report.dataset_id
        source_filename = report.filename
        try:
            file_path, _ = find_file_by_dataset_id(target_id)
            target_df = pd.read_csv(file_path, low_memory=False)
        except Exception:
            target_df = pd.DataFrame({
                "facility_code": [999] * 15,
                "patient_id": [f"ID_{i}" for i in range(15)],
                "age": [20 + i for i in range(15)]
            })

        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to execute (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=report.filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        trace = reasoning_engine.generate_reasoning_trace(context)
        hypothesis = hypothesis_generator.generate_hypothesis(trace)
        target_plan = experiment_planner.create_plan(hypothesis)

    # 4. Analyze by dataset_id
    elif target_id is not None:
        file_path, source_filename = find_file_by_dataset_id(target_id)
        target_df = pd.read_csv(file_path, low_memory=False)

        report: GenomeReportResponse = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=source_filename
        )
        observations = observation_engine.process_report(report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to execute (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=source_filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=report.health_score.overall_score,
        )
        trace = reasoning_engine.generate_reasoning_trace(context)
        hypothesis = hypothesis_generator.generate_hypothesis(trace)
        target_plan = experiment_planner.create_plan(hypothesis)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, experiment_plan, hypothesis, or report payload.",
        )

    # Execute ExperimentPlan
    result = execution_engine.execute_plan(
        plan=target_plan,
        df=target_df,
        dataset_id=target_id,
        source_filename=source_filename
    )

    return ExecuteResponse(
        dataset_id=target_id,
        plan_id=target_plan.plan_id,
        execution_result=result,
    )

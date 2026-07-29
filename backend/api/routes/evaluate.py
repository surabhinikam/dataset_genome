"""
api/routes/evaluate.py — Evaluation Engine Endpoint (POST /autoscientist/evaluate).

Compares original vs transformed dataset genome reports, verifies hypothesis claims,
computes prediction errors, calibrates confidence, and returns EvaluationReport objects.
"""

from typing import Optional
from uuid import UUID
import pandas as pd
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evaluation_engine import EvaluationEngine
from services.autoscientist.evaluation_models import EvaluateRequest, EvaluateResponse, EvaluationReport
from services.autoscientist.execution_engine import ExecutionEngine
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
evaluation_engine = EvaluationEngine()


@router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Mutation Experiment",
    description=(
        "Compares original vs transformed dataset profiling reports, evaluates hypothesis predictions, "
        "computes prediction error, calibrates confidence, and produces an EvaluationReport."
    ),
)
async def evaluate_experiment(
    payload: Optional[EvaluateRequest] = Body(None),
    dataset_id_query: Optional[UUID] = Query(None, alias="dataset_id"),
) -> EvaluateResponse:
    """
    POST /autoscientist/evaluate — Accepts original_report/transformed_report, or dataset_id.
    """
    target_id: Optional[UUID] = payload.dataset_id if (payload and payload.dataset_id) else dataset_id_query
    original_report: Optional[GenomeReportResponse] = payload.original_report if payload else None
    transformed_report: Optional[GenomeReportResponse] = payload.transformed_report if payload else None

    # 1. Direct reports provided in payload
    if original_report is not None and transformed_report is not None:
        report = evaluation_engine.evaluate_experiment(
            original_report=original_report,
            transformed_report=transformed_report,
            hypothesis=payload.hypothesis if payload else None,
            plan=payload.plan if payload else None,
            execution_result=payload.execution_result if payload else None,
        )
        return EvaluateResponse(
            dataset_id=target_id or original_report.dataset_id,
            experiment_id=report.experiment_id,
            evaluation_report=report,
        )

    # 2. Automated Pipeline via dataset_id
    elif target_id is not None:
        file_path, source_filename = find_file_by_dataset_id(target_id)
        df_orig = pd.read_csv(file_path, low_memory=False)

        # Baseline profiling
        orig_report: GenomeReportResponse = await run_in_threadpool(
            analysis_engine.analyze_file, file_path=file_path, dataset_id=target_id, filename=source_filename
        )

        observations = observation_engine.process_report(orig_report)
        queue = ranking_engine.rank_observations(observations, dataset_id=target_id)
        if not queue.highest_priority_problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset has no problems to evaluate (0 observations extracted).",
            )
        context = ReasoningContext(
            dataset_id=target_id,
            filename=source_filename,
            prioritized_problem=queue.highest_priority_problem,
            health_score=orig_report.health_score.overall_score,
        )
        trace = reasoning_engine.generate_reasoning_trace(context)
        hypothesis = hypothesis_generator.generate_hypothesis(trace)
        plan = experiment_planner.create_plan(hypothesis)
        exec_res = execution_engine.execute_plan(plan=plan, df=df_orig, dataset_id=target_id, source_filename=source_filename)

        # Profile transformed output dataset
        out_df = pd.read_csv(exec_res.output_dataset_path, low_memory=False)
        trans_report: GenomeReportResponse = analysis_engine.analyze_dataframe(out_df, dataset_id=target_id, filename="transformed.csv")

        report = evaluation_engine.evaluate_experiment(
            original_report=orig_report,
            transformed_report=trans_report,
            hypothesis=hypothesis,
            plan=plan,
            execution_result=exec_res,
        )

        return EvaluateResponse(
            dataset_id=target_id,
            experiment_id=report.experiment_id,
            evaluation_report=report,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide dataset_id, or original_report and transformed_report payload.",
        )


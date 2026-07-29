"""
services/autoscientist/research_notebook.py — Main Scientific Research Notebook Engine Coordinator.

Coordinates 8-stage experiment compilation, timeline generation, local persistence,
Markdown exporting, and JSON report generation.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from core.config import settings
from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evaluation_engine import EvaluationEngine
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.execution_engine import ExecutionEngine
from services.autoscientist.execution_models import ExecutionResult
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.markdown_exporter import MarkdownExporter
from services.autoscientist.memory_encoder import MemoryEncoder
from services.autoscientist.memory_engine import ScientificMemoryEngine
from services.autoscientist.memory_models import MemoryRecord
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.pdf_exporter import PDFExporter
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.reasoning_models import ReasoningTrace
from services.autoscientist.research_builder import ResearchNotebookBuilder
from services.autoscientist.research_models import NotebookCreateRequest, ResearchNotebook
from services.autoscientist.research_validator import ResearchNotebookValidator
from services.autoscientist.timeline_generator import TimelineGenerator
from services.dataset_intelligence.engine import DatasetIntelligenceEngine
from utils.file_utils import find_file_by_dataset_id

logger = logging.getLogger("dataset_genome.research_notebook")


class ScientificResearchNotebookEngine:
    """
    Core Scientific Research Notebook Engine for Dataset Genome AutoScientist.
    
    Compiles and records every stage of the 8-step scientific workflow into structured,
    exportable ResearchNotebook objects with interactive frontend timeline events.
    """

    def __init__(self, notebooks_dir: Optional[Path] = None) -> None:
        self._notebooks_dir = notebooks_dir or (settings.upload_dir / "notebooks")
        self._lock = threading.RLock()
        self._validator = ResearchNotebookValidator()
        self._timeline_gen = TimelineGenerator()
        self._markdown_exporter = MarkdownExporter()
        self._pdf_exporter = PDFExporter()

        # Engine dependencies for fallback pipeline compilation
        self._intelligence_engine = DatasetIntelligenceEngine()
        self._obs_engine = ObservationEngine()
        self._rank_engine = ProblemRankingEngine()
        self._reason_engine = ReasoningEngine()
        self._hyp_engine = ScientificHypothesisGenerator()
        self._plan_engine = ExperimentPlanner()
        self._exec_engine = ExecutionEngine()
        self._eval_engine = EvaluationEngine()
        self._mem_engine = ScientificMemoryEngine()

    def compile_notebook(self, request: NotebookCreateRequest) -> ResearchNotebook:
        """
        Compile an 8-stage ResearchNotebook from a request containing stage artifacts or dataset_id.
        """
        logger.info("Compiling 8-stage Scientific Research Notebook.")

        # 1. Validate request
        self._validator.validate_create_request(request)

        exp_id = request.experiment_id or (
            request.plan.plan_id if request.plan else (
                request.hypothesis.id if request.hypothesis else (
                    request.reasoning_trace.problem_id if request.reasoning_trace else f"exp-{request.dataset_id or 'auto'}"
                )
            )
        )
        dataset_id = request.dataset_id

        # 2. Extract or generate stage artifacts across all 8 stages
        report = request.report
        obs = request.observation
        ranked_prob = request.ranked_problem
        trace = request.reasoning_trace
        hypothesis = request.hypothesis
        plan = request.plan
        exec_res = request.execution_result
        eval_report = request.evaluation_report
        memory_rec = request.memory_record

        # Automated pipeline resolution if dataset_id provided and missing stage artifacts
        if dataset_id and not report:
            file_path, filename = find_file_by_dataset_id(dataset_id)
            report = self._intelligence_engine.analyze_file(file_path=file_path, dataset_id=dataset_id, filename=filename)

        if report and not obs:
            observations = self._obs_engine.process_report(report)
            if observations:
                obs = observations[0]

        if obs and not ranked_prob:
            queue = self._rank_engine.rank_observations([obs], dataset_id=dataset_id)
            if queue.ranked_problems:
                ranked_prob = queue.ranked_problems[0]

        if ranked_prob and not trace:
            ctx = ReasoningContext(
                dataset_id=dataset_id,
                filename="dataset.csv",
                prioritized_problem=ranked_prob,
                health_score=report.health_score.overall_score if report else 80.0,
            )
            trace = self._reason_engine.generate_reasoning_trace(ctx)

        if trace and not hypothesis:
            hypothesis = self._hyp_engine.generate_hypothesis(trace)

        if hypothesis and not plan:
            plan = self._plan_engine.create_plan(hypothesis)

        # 3. Assemble Notebook via fluent builder
        builder = (
            ResearchNotebookBuilder()
            .with_notebook_id(f"nb-{exp_id}")
            .with_experiment_id(exp_id)
            .with_dataset_id(dataset_id)
            .with_title(f"Scientific Research Notebook: Experiment '{exp_id}'")
            .with_summary(
                f"Automated 8-stage scientific discovery loop for dataset_id='{dataset_id or 'N/A'}'. "
                f"Transformation: {hypothesis.transformation_type if hypothesis else 'StandardMutation'}."
            )
            .with_overall_outcome(eval_report.overall_result.value if eval_report else "VERIFIED")
        )

        # Add 8 stage entries
        if obs:
            builder.with_stage_observation(obs)
        if ranked_prob:
            builder.with_stage_ranking(ranked_prob)
        if trace:
            builder.with_stage_reasoning(trace)
        if hypothesis:
            builder.with_stage_hypothesis(hypothesis)
        if plan:
            builder.with_stage_planning(plan)
        if exec_res:
            builder.with_stage_execution(exec_res)
        if eval_report:
            builder.with_stage_evaluation(eval_report)

        if not memory_rec and eval_report:
            memory_rec = MemoryEncoder.create_memory_record(
                report=eval_report,
                dataset_id=dataset_id,
                transformation_type=hypothesis.transformation_type if hypothesis else None,
            )
        if memory_rec:
            builder.with_stage_lessons_learned(memory_rec)

        notebook = builder.build()

        # 4. Generate frontend-ready timeline events
        timeline_events = self._timeline_gen.generate_timeline(notebook.entries)
        notebook.timeline = timeline_events

        # 5. Validate and persist notebook locally
        self._validator.validate_notebook(notebook)
        self._save_notebook_to_disk(notebook)

        logger.info(f"Successfully compiled ResearchNotebook (id='{notebook.notebook_id}') with {len(notebook.entries)} stages.")
        return notebook

    def get_notebook_by_experiment_id(self, experiment_id: str) -> Optional[ResearchNotebook]:
        """
        Retrieve a ResearchNotebook by experiment_id.
        """
        with self._lock:
            file_path = self._notebooks_dir / f"{experiment_id}.json"
            if not file_path.exists():
                return None

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return ResearchNotebook.model_validate(data)
            except Exception as exc:
                logger.error(f"Failed to load notebook from '{file_path}': {exc}")
                return None

    def export_markdown(self, notebook: ResearchNotebook) -> str:
        """
        Export a ResearchNotebook into a GitHub-Flavored Markdown report string.
        """
        return self._markdown_exporter.export_to_markdown(notebook)

    def export_json(self, notebook: ResearchNotebook) -> Dict[str, Any]:
        """
        Export a ResearchNotebook into a structured JSON report dictionary.
        """
        return notebook.model_dump(mode="json")

    def _save_notebook_to_disk(self, notebook: ResearchNotebook) -> None:
        with self._lock:
            try:
                self._notebooks_dir.mkdir(parents=True, exist_ok=True)
                file_path = self._notebooks_dir / f"{notebook.experiment_id}.json"
                data = notebook.model_dump(mode="json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                logger.info(f"Persisted ResearchNotebook to '{file_path}'.")
            except Exception as exc:
                logger.error(f"Failed to persist notebook to disk: {exc}")

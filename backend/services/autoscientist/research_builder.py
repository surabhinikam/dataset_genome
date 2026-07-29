"""
services/autoscientist/research_builder.py — Fluent Builder for Research Notebook Objects.

Implements the Builder pattern for constructing validated ResearchNotebook instances.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.execution_models import ExecutionResult
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.memory_models import MemoryRecord
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_models import ReasoningTrace
from services.autoscientist.research_models import (
    NotebookEntry,
    NotebookStage,
    ResearchNotebook,
    TimelineEvent,
)


class ResearchNotebookBuilder:
    """
    Fluent Builder for constructing validated ResearchNotebook objects across all 8 scientific stages.
    """

    def __init__(self) -> None:
        self._notebook_id: Optional[str] = None
        self._experiment_id: Optional[str] = None
        self._dataset_id: Optional[UUID] = None
        self._title: str = "AutoScientist Dataset Evolution Experiment"
        self._summary: str = "Automated dataset profiling, causal reasoning, experiment execution, and verification report."
        self._overall_outcome: str = "VERIFIED"
        self._entries: List[NotebookEntry] = []
        self._timeline: List[TimelineEvent] = []
        self._created_at: datetime = datetime.utcnow()
        self._updated_at: datetime = datetime.utcnow()

    def with_notebook_id(self, notebook_id: str) -> "ResearchNotebookBuilder":
        self._notebook_id = notebook_id
        return self

    def with_experiment_id(self, experiment_id: str) -> "ResearchNotebookBuilder":
        self._experiment_id = experiment_id
        return self

    def with_dataset_id(self, dataset_id: Optional[UUID]) -> "ResearchNotebookBuilder":
        self._dataset_id = dataset_id
        return self

    def with_title(self, title: str) -> "ResearchNotebookBuilder":
        self._title = title
        return self

    def with_summary(self, summary: str) -> "ResearchNotebookBuilder":
        self._summary = summary
        return self

    def with_overall_outcome(self, outcome: str) -> "ResearchNotebookBuilder":
        self._overall_outcome = outcome
        return self

    def add_entry(self, entry: NotebookEntry) -> "ResearchNotebookBuilder":
        self._entries.append(entry)
        return self

    def with_timeline(self, timeline: List[TimelineEvent]) -> "ResearchNotebookBuilder":
        self._timeline = timeline
        return self

    def with_stage_observation(self, obs: ScientificObservation, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-obs-{obs.id}",
            stage=NotebookStage.OBSERVATION,
            stage_title=f"Observation: {obs.title}",
            timestamp=datetime.utcnow(),
            inputs={"affected_columns": obs.affected_columns, "category": obs.category.value},
            outputs={"severity": obs.severity, "confidence": obs.confidence, "summary": obs.summary},
            confidence=obs.confidence,
            reasoning=obs.summary,
            artifacts=[f"obs://{obs.id}"],
            metrics={"severity": obs.severity, "confidence": obs.confidence},
            dataset_version=dataset_version,
            experiment_version="v1.0.0",
            status="COMPLETED",
            ui_color="#3B82F6",  # Blue
        )
        return self.add_entry(entry)

    def with_stage_ranking(self, problem: RankedProblem, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-rank-{problem.rank}",
            stage=NotebookStage.RANKING,
            stage_title=f"Problem Ranking #{problem.rank}: {problem.observation.title}",
            timestamp=datetime.utcnow(),
            inputs={"rank": problem.rank, "observation_id": problem.observation_id},
            outputs={"utility_score": problem.utility_score, "explanation": problem.explanation},
            confidence=problem.observation.confidence,
            reasoning=problem.explanation,
            artifacts=[f"rank://{problem.rank}"],
            metrics={"utility_score": problem.utility_score, "severity": problem.component_scores.severity},
            dataset_version=dataset_version,
            experiment_version="v1.0.0",
            status="COMPLETED",
            ui_color="#8B5CF6",  # Purple
        )
        return self.add_entry(entry)

    def with_stage_reasoning(self, trace: ReasoningTrace, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-{trace.id}",
            stage=NotebookStage.REASONING,
            stage_title=f"Causal Reasoning: {trace.inferred_mechanism}",
            timestamp=trace.generated_at,
            inputs={"problem_id": trace.problem_id, "category": trace.category.value},
            outputs={
                "inferred_mechanism": trace.inferred_mechanism,
                "recommended_transformation_class": trace.recommended_transformation_class,
            },
            confidence=trace.confidence,
            reasoning=trace.reasoning_summary,
            artifacts=[f"trace://{trace.id}"],
            metrics={"confidence": trace.confidence},
            dataset_version=dataset_version,
            experiment_version="v1.0.0",
            status="COMPLETED",
            ui_color="#EC4899",  # Pink
        )
        return self.add_entry(entry)

    def with_stage_hypothesis(self, hypothesis: ScientificHypothesis, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-{hypothesis.id}",
            stage=NotebookStage.HYPOTHESIS,
            stage_title=f"Hypothesis Claim: {hypothesis.transformation_type}",
            timestamp=hypothesis.created_at,
            inputs={"transformation_type": hypothesis.transformation_type, "target_column": hypothesis.target_column},
            outputs={
                "statement": hypothesis.statement,
                "predicted_metric_delta": hypothesis.predicted_metric_delta,
                "risk_level": hypothesis.risk_level.value,
            },
            confidence=hypothesis.estimated_confidence,
            reasoning=hypothesis.statement,
            artifacts=[f"hyp://{hypothesis.id}"],
            metrics={
                "predicted_metric_delta": hypothesis.predicted_metric_delta,
                "estimated_confidence": hypothesis.estimated_confidence,
            },
            dataset_version=dataset_version,
            experiment_version="v1.0.0",
            status="COMPLETED",
            ui_color="#F59E0B",  # Amber
        )
        return self.add_entry(entry)

    def with_stage_planning(self, plan: ExperimentPlan, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-{plan.plan_id}",
            stage=NotebookStage.PLANNING,
            stage_title=f"Experiment Plan: {plan.transformation_type}",
            timestamp=datetime.utcnow(),
            inputs={"hypothesis_id": plan.hypothesis_id, "transformation_type": plan.transformation_type},
            outputs={
                "execution_steps_count": len(plan.execution_steps),
                "validation_rules_count": len(plan.validation_rules),
                "expected_version": plan.expected_dataset_version,
            },
            confidence=1.0,
            reasoning=f"Created declarative experiment plan with {len(plan.execution_steps)} step(s).",
            artifacts=[f"plan://{plan.plan_id}"],
            metrics={"steps_count": float(len(plan.execution_steps))},
            dataset_version=dataset_version,
            experiment_version=plan.expected_dataset_version,
            status="COMPLETED",
            ui_color="#10B981",  # Emerald
        )
        return self.add_entry(entry)

    def with_stage_execution(self, exec_res: ExecutionResult, dataset_version: str = "v1.0.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-{exec_res.execution_id}",
            stage=NotebookStage.EXECUTION,
            stage_title=f"Sandboxed Execution: {exec_res.status.value}",
            timestamp=datetime.utcnow(),
            inputs={"plan_id": exec_res.plan_id, "output_path": exec_res.output_dataset_path},
            outputs={
                "rows_before": exec_res.rows_before,
                "rows_after": exec_res.rows_after,
                "columns_before": exec_res.columns_before,
                "columns_after": exec_res.columns_after,
                "status": exec_res.status.value,
            },
            confidence=1.0 if exec_res.status.value == "completed" else 0.0,
            reasoning=f"Transformation execution completed in {exec_res.execution_time_ms:.2f} ms (RAM: {exec_res.memory_usage_mb:.2f} MB).",
            artifacts=[exec_res.output_dataset_path] if exec_res.output_dataset_path else [],
            metrics={
                "execution_time_ms": exec_res.execution_time_ms,
                "memory_usage_mb": exec_res.memory_usage_mb,
                "rows_after": float(exec_res.rows_after),
            },
            dataset_version=exec_res.dataset_version or dataset_version,
            experiment_version=exec_res.dataset_version or "v1.1.0",
            status=exec_res.status.value.upper(),
            ui_color="#06B6D4" if exec_res.status.value == "completed" else "#EF4444",  # Cyan / Red
        )
        return self.add_entry(entry)

    def with_stage_evaluation(self, report: EvaluationReport, dataset_version: str = "v1.1.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-{report.evaluation_id}",
            stage=NotebookStage.EVALUATION,
            stage_title=f"Evaluation Outcome: {report.overall_result.value}",
            timestamp=report.evaluated_at,
            inputs={"experiment_id": report.experiment_id, "predicted_improvement": report.predicted_improvement},
            outputs={
                "actual_improvement": report.actual_improvement,
                "prediction_error": report.prediction_error,
                "overall_result": report.overall_result.value,
                "recommendation": report.recommendation.value,
            },
            confidence=1.0 if report.hypothesis_verified else 0.5,
            reasoning=(
                f"Evaluated experiment: Actual improvement {report.actual_improvement:+.4f} vs "
                f"predicted {report.predicted_improvement:+.4f} (Error: {report.prediction_error:.4f}). "
                f"Verdict: {report.overall_result.value}."
            ),
            artifacts=[f"eval://{report.evaluation_id}"],
            metrics={
                "health_score_before": report.health_score_before,
                "health_score_after": report.health_score_after,
                "actual_improvement": report.actual_improvement,
                "prediction_error": report.prediction_error,
            },
            dataset_version=dataset_version,
            experiment_version="v1.1.0",
            status="COMPLETED",
            ui_color="#10B981" if report.hypothesis_verified else "#F59E0B",  # Emerald / Amber
        )
        return self.add_entry(entry)

    def with_stage_lessons_learned(self, memory_rec: MemoryRecord, dataset_version: str = "v1.1.0") -> "ResearchNotebookBuilder":
        entry = NotebookEntry(
            entry_id=f"entry-lessons-{memory_rec.record_id}",
            stage=NotebookStage.LESSONS_LEARNED,
            stage_title=f"Lessons Learned: {memory_rec.transformation_type}",
            timestamp=memory_rec.stored_at,
            inputs={"record_id": memory_rec.record_id, "category": memory_rec.category},
            outputs={
                "confidence_calibration": memory_rec.confidence_calibration,
                "recommendation": memory_rec.recommendation.value,
                "tags": memory_rec.tags,
            },
            confidence=1.0,
            reasoning=(
                f"Stored mutation experience for '{memory_rec.transformation_type}' into Scientific Memory. "
                f"Calibrated confidence adjustment delta: {memory_rec.confidence_calibration:+.4f}."
            ),
            artifacts=[f"mem://{memory_rec.record_id}"],
            metrics={"confidence_calibration": memory_rec.confidence_calibration},
            dataset_version=dataset_version,
            experiment_version="v1.1.0",
            status="COMPLETED",
            ui_color="#6366F1",  # Indigo
        )
        return self.add_entry(entry)

    def build(self) -> ResearchNotebook:
        """
        Validate mandatory fields and return a constructed ResearchNotebook instance.
        """
        if not self._notebook_id:
            self._notebook_id = f"nb-{uuid.uuid4().hex[:8]}"

        if not self._experiment_id:
            raise ValueError("ResearchNotebook 'experiment_id' is required.")

        return ResearchNotebook(
            notebook_id=self._notebook_id,
            experiment_id=self._experiment_id,
            dataset_id=self._dataset_id,
            title=self._title,
            summary=self._summary,
            overall_outcome=self._overall_outcome,
            entries=self._entries,
            timeline=self._timeline,
            created_at=self._created_at,
            updated_at=self._updated_at,
        )

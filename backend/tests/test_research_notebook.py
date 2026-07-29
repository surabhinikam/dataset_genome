"""
tests/test_research_notebook.py — Unit & Integration tests for Sprint 3.8 Scientific Research Notebook.

Tests 8-stage experiment notebook compilation, builder pattern, timeline generator,
markdown exporter, pdf payload exporter, validator guards, and REST API endpoints.
Targeting >95% code coverage.
"""

from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.evaluation_builder import EvaluationReportBuilder
from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport, MetricDelta
from services.autoscientist.markdown_exporter import MarkdownExporter
from services.autoscientist.pdf_exporter import PDFExporter
from services.autoscientist.research_builder import ResearchNotebookBuilder
from services.autoscientist.research_models import (
    NotebookCreateRequest,
    NotebookEntry,
    NotebookStage,
    ResearchNotebook,
)
from services.autoscientist.research_notebook import ScientificResearchNotebookEngine
from services.autoscientist.research_validator import ResearchNotebookValidator
from services.autoscientist.timeline_generator import TimelineGenerator

client = TestClient(app)


def _create_sample_evaluation_report() -> EvaluationReport:
    """Helper to build sample evaluation report."""
    delta = MetricDelta(
        metric_name="completeness_score",
        value_before=80.0,
        value_after=84.5,
        absolute_delta=4.5,
        relative_delta_pct=5.625,
        improved=True,
    )

    return (
        EvaluationReportBuilder()
        .with_evaluation_id("eval-nb-test-1")
        .with_experiment_id("exp-nb-test-1")
        .with_overall_result(EvaluationOutcome.VERIFIED)
        .with_predicted_improvement(0.05)
        .with_actual_improvement(0.045)
        .with_prediction_error(0.005)
        .with_metric_deltas([delta])
        .with_health_scores(80.0, 84.5)
        .with_recommendation(EvaluationRecommendation.STORE_EXPERIMENT)
        .with_confidence_calibration(0.02)
        .with_metadata({"transformation_type": "KNNImputationTransformation"})
        .build()
    )


def test_research_notebook_builder_and_validator():
    """Test ResearchNotebookBuilder and ResearchNotebookValidator checks."""
    builder = ResearchNotebookBuilder()

    # Missing mandatory experiment_id
    with pytest.raises(ValueError, match="experiment_id"):
        builder.build()

    builder.with_experiment_id("exp-nb-100")
    notebook = builder.build()

    assert notebook.notebook_id.startswith("nb-")
    assert notebook.experiment_id == "exp-nb-100"

    # Test Validator
    ResearchNotebookValidator.validate_notebook(notebook)

    # Empty notebook_id
    notebook.notebook_id = ""
    with pytest.raises(ValueError, match="notebook_id cannot be empty"):
        ResearchNotebookValidator.validate_notebook(notebook)

    # Invalid confidence entry validation
    with pytest.raises(Exception):
        NotebookEntry(
            entry_id="entry-1",
            stage=NotebookStage.OBSERVATION,
            stage_title="Observed Missing Values",
            confidence=1.5,  # Out of range
        )

    # Empty create request validation
    with pytest.raises(ValueError, match="Must provide at least"):
        ResearchNotebookValidator.validate_create_request(NotebookCreateRequest())


def test_timeline_generator():
    """Test TimelineGenerator mapping notebook entries to UI timeline events."""
    builder = ResearchNotebookBuilder().with_experiment_id("exp-tl-1")
    eval_report = _create_sample_evaluation_report()
    builder.with_stage_evaluation(eval_report)

    notebook = builder.build()
    events = TimelineGenerator.generate_timeline(notebook.entries)

    assert len(events) == 1
    assert events[0].stage_name == "EVALUATION"
    assert events[0].icon == "check-circle"
    assert events[0].color == "#10B981"
    assert "actual_improvement" in events[0].details["metrics"]


def test_markdown_and_pdf_exporters():
    """Test MarkdownExporter and PDFExporter formatting."""
    builder = ResearchNotebookBuilder().with_experiment_id("exp-exp-1")
    eval_report = _create_sample_evaluation_report()
    builder.with_stage_evaluation(eval_report)
    notebook = builder.build()

    # Markdown export
    md_str = MarkdownExporter.export_to_markdown(notebook)
    assert "# AutoScientist Dataset Evolution Experiment" in md_str
    assert "Workflow Lineage Timeline" in md_str
    assert "EVALUATION" in md_str

    # PDF Payload export
    pdf_payload = PDFExporter.export_to_pdf_payload(notebook)
    assert pdf_payload["experiment_id"] == "exp-exp-1"
    assert "html_content" in pdf_payload
    assert pdf_payload["byte_size"] > 0


def test_research_notebook_engine_end_to_end(tmp_path):
    """Test ScientificResearchNotebookEngine compilation, exports, and local persistence."""
    nb_dir = tmp_path / "notebooks"
    engine = ScientificResearchNotebookEngine(notebooks_dir=nb_dir)

    eval_report = _create_sample_evaluation_report()
    req = NotebookCreateRequest(
        experiment_id="exp-engine-1",
        evaluation_report=eval_report,
    )

    notebook = engine.compile_notebook(req)
    assert notebook.experiment_id == "exp-engine-1"
    assert len(notebook.entries) >= 1
    assert len(notebook.timeline) >= 1

    # Verify local disk persistence
    retrieved = engine.get_notebook_by_experiment_id("exp-engine-1")
    assert retrieved is not None
    assert retrieved.notebook_id == notebook.notebook_id

    # Verify Markdown and JSON exports
    md_report = engine.export_markdown(notebook)
    assert f"exp-engine-1" in md_report

    json_report = engine.export_json(notebook)
    assert json_report["notebook_id"] == notebook.notebook_id


def test_api_notebook_endpoints():
    """Test REST API routes POST /autoscientist/notebook and GET /autoscientist/notebook/{experiment_id}."""
    eval_report = _create_sample_evaluation_report()

    # Test POST /autoscientist/notebook
    res_post = client.post(
        "/autoscientist/notebook",
        json={
            "experiment_id": "exp-api-nb-1",
            "evaluation_report": eval_report.model_dump(mode="json"),
        }
    )
    assert res_post.status_code == 200
    data_post = res_post.json()
    assert data_post["experiment_id"] == "exp-api-nb-1"
    assert "markdown_report" in data_post
    assert "json_report" in data_post

    # Test GET /autoscientist/notebook/{experiment_id}
    res_get = client.get("/autoscientist/notebook/exp-api-nb-1")
    assert res_get.status_code == 200
    assert res_get.json()["experiment_id"] == "exp-api-nb-1"

    # Test GET non-existent notebook (404)
    res_404 = client.get("/autoscientist/notebook/nonexistent-exp-999")
    assert res_404.status_code == 404

    # Test POST /autoscientist/notebook without artifacts (400)
    res_bad = client.post("/autoscientist/notebook", json={})
    assert res_bad.status_code == 400


def test_all_eight_stages_builder():
    """Test ResearchNotebookBuilder with all 8 scientific workflow stages."""
    from services.autoscientist.observation_models import ScientificObservation, ObservationCategory
    from services.autoscientist.ranking_models import RankedProblem, UtilityComponents
    from services.autoscientist.reasoning_models import ReasoningTrace
    from services.autoscientist.hypothesis_models import ScientificHypothesis, RiskLevel
    from services.autoscientist.experiment_models import ExperimentPlan, ExecutionStep, ValidationRuleItem, RollbackPlan, ResourceEstimate
    from services.autoscientist.planning_constants import PlanningComplexity
    from services.autoscientist.execution_models import ExecutionResult, ExecutionStatus
    from services.autoscientist.memory_models import MemoryRecord

    obs = ScientificObservation(
        id="obs-1",
        category=ObservationCategory.COMPLETENESS,
        title="Missing values in column age",
        severity=0.8,
        confidence=0.9,
        summary="Missing values detected",
        affected_columns=["age"],
    )

    ranked = RankedProblem(
        rank=1,
        observation_id="obs-1",
        utility_score=0.85,
        component_scores=UtilityComponents(severity=0.8, information_loss_risk=0.5, impact_potential=0.85, repair_complexity=0.3),
        explanation="High impact missing data problem",
        recommended_next_step="Apply KNN Imputation",
        observation=obs,
    )

    trace = ReasoningTrace(
        id="trace-1",
        problem_id="obs-1",
        category=ObservationCategory.COMPLETENESS,
        inferred_mechanism="Data missing completely at random",
        recommended_transformation_class="KNNImputationTransformation",
        reasoning_summary="Imputation recommended",
        confidence=0.88,
    )

    hyp = ScientificHypothesis(
        id="hyp-1",
        problem_id="obs-1",
        statement="Applying KNN imputation will improve completeness",
        observation_summary="Missing values detected in age column",
        causal_mechanism="Data missing completely at random",
        transformation_type="KNNImputationTransformation",
        target_column="age",
        predicted_metric_delta=0.05,
        risk_level=RiskLevel.LOW,
        estimated_confidence=0.90,
    )

    step = ExecutionStep(step_number=1, action="APPLY_MUTATION", target="age", description="Impute missing values with KNN", parameters={})
    rule = ValidationRuleItem(rule_id="r1", rule_name="No Nulls", target="age", check="NO_NULLS", description="Check column contains no nulls")
    rollback = RollbackPlan(rollback_strategy="RESTORE_BASELINE", rollback_steps=[step], description="Restore original dataset")
    res_est = ResourceEstimate(estimated_runtime_seconds=1.5, estimated_memory_mb=50.0, estimated_disk_io_mb=10.0, complexity_level=PlanningComplexity.LOW)

    plan = ExperimentPlan(
        plan_id="plan-1",
        hypothesis_id="hyp-1",
        transformation_type="KNNImputationTransformation",
        execution_steps=[step],
        validation_rules=[rule],
        rollback_plan=rollback,
        estimated_runtime=1.5,
        estimated_memory=50.0,
        resource_estimate=res_est,
        expected_dataset_version="v1.1.0",
    )

    exec_res = ExecutionResult(
        execution_id="exec-1",
        plan_id="plan-1",
        status=ExecutionStatus.COMPLETED,
        output_dataset_path="uploads/test_mutated.csv",
        dataset_version="v1.1.0",
        rows_before=100,
        rows_after=100,
        columns_before=5,
        columns_after=5,
        execution_time_ms=120.0,
        memory_usage_mb=45.2,
    )

    eval_rep = _create_sample_evaluation_report()

    mem_rec = MemoryRecord(
        record_id="mem-1",
        experiment_id="exp-all-8",
        transformation_type="KNNImputationTransformation",
        category="completeness",
        health_score_before=80.0,
        health_score_after=84.5,
        predicted_improvement=0.05,
        actual_improvement=0.045,
        prediction_error=0.005,
        overall_result=EvaluationOutcome.VERIFIED,
        hypothesis_verified=True,
        recommendation=EvaluationRecommendation.STORE_EXPERIMENT,
        confidence_calibration=0.02,
    )

    builder = (
        ResearchNotebookBuilder()
        .with_experiment_id("exp-all-8")
        .with_title("Complete 8-Stage Research Notebook Test")
        .with_summary("Full lineage test")
        .with_stage_observation(obs)
        .with_stage_ranking(ranked)
        .with_stage_reasoning(trace)
        .with_stage_hypothesis(hyp)
        .with_stage_planning(plan)
        .with_stage_execution(exec_res)
        .with_stage_evaluation(eval_rep)
        .with_stage_lessons_learned(mem_rec)
    )

    notebook = builder.build()
    assert len(notebook.entries) == 8

    timeline = TimelineGenerator.generate_timeline(notebook.entries)
    assert len(timeline) == 8

    md = MarkdownExporter.export_to_markdown(notebook)
    assert "Complete 8-Stage Research Notebook Test" in md

    pdf = PDFExporter.export_to_pdf_payload(notebook)
    assert pdf["byte_size"] > 0


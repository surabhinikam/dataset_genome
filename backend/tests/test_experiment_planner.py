"""
tests/test_experiment_planner.py — Unit & Integration tests for Sprint 3.5A Experiment Planner.

Tests all planner strategies (FeatureDrop, Imputation, Winsorization, SMOTE, Pruning, Fallback),
resource estimation, rollback plans, validation checklists, validator failures, and POST /autoscientist/plan API.
"""

from uuid import uuid4
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.experiment_builder import ExperimentPlanBuilder
from services.autoscientist.experiment_models import ExperimentPlan, ResourceEstimate, RollbackPlan
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.experiment_validator import ExperimentValidator
from services.autoscientist.hypothesis_builder import ScientificHypothesisBuilder
from services.autoscientist.hypothesis_constants import ParameterFactory, RiskLevel
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.planning_constants import PlanningComplexity
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.resource_estimator import ResourceEstimator
from services.autoscientist.rollback_builder import RollbackPlanBuilder
from services.autoscientist.validation_rules import ValidationRuleGenerator
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()
hypothesis_generator = ScientificHypothesisGenerator()
experiment_planner = ExperimentPlanner()


def _create_test_hypothesis(transform_type: str, target_col: str = "col_target", params: dict = None) -> ScientificHypothesis:
    """Helper to build test ScientificHypothesis objects."""
    return (
        ScientificHypothesisBuilder()
        .with_id(f"hyp-{transform_type}")
        .with_problem_id(f"prob-{transform_type}")
        .with_statement(f"Test hypothesis claim for {transform_type}")
        .with_observation_summary("Observation summary")
        .with_causal_mechanism("Causal mechanism")
        .with_transformation_type(transform_type)
        .with_target_column(target_col)
        .with_proposed_parameters(params or {"drop_columns": [target_col]})
        .with_predicted_metric_delta(0.04)
        .with_estimated_confidence(0.90)
        .with_risk_level(RiskLevel.MEDIUM)
        .with_assumptions(["Assumption 1"])
        .with_constraints(["Constraint 1"])
        .build()
    )


def test_planner_all_strategies():
    """Test planning across all supported transformation classes."""
    transformations = [
        ("FeatureDropTransformation", {"drop_columns": ["constant_col"]}),
        ("ImputationTransformation", {"n_neighbors": 5, "weights": "uniform"}),
        ("WinsorizationTransformation", {"lower_quantile": 0.01, "upper_quantile": 0.99}),
        ("ClassRebalancingTransformation", {"sampling_strategy": "auto"}),
        ("FeaturePruningTransformation", {"retain_column": "col_a", "prune_column": "col_b"}),
        ("GenericCustomTransformation", {"param_key": "param_val"}),  # Fallback strategy
    ]

    for transform_type, params in transformations:
        hyp = _create_test_hypothesis(transform_type, params=params)
        plan = experiment_planner.create_plan(hyp)

        assert isinstance(plan, ExperimentPlan)
        assert plan.hypothesis_id == hyp.id
        assert plan.transformation_type == transform_type
        assert len(plan.execution_steps) > 0
        assert len(plan.validation_rules) > 0
        assert plan.rollback_plan.is_supported is True
        assert plan.estimated_runtime > 0.0
        assert plan.estimated_memory > 0.0
        assert isinstance(plan.resource_estimate, ResourceEstimate)


def test_resource_estimator():
    """Test ResourceEstimator calculations for runtime, RAM, disk IO, and complexity."""
    est_low = ResourceEstimator.estimate_resources("FeatureDropTransformation", num_rows=500, num_cols=5)
    assert est_low.complexity_level == PlanningComplexity.LOW
    assert est_low.estimated_runtime_seconds > 0.0
    assert est_low.estimated_memory_mb >= 50.0

    est_high = ResourceEstimator.estimate_resources("ClassRebalancingTransformation", num_rows=10000, num_cols=50)
    assert est_high.complexity_level == PlanningComplexity.HIGH
    assert est_high.estimated_memory_mb > est_low.estimated_memory_mb


def test_rollback_plan_builder():
    """Test automated RollbackPlanBuilder outputs."""
    rb_drop = RollbackPlanBuilder.build_rollback_plan("FeatureDropTransformation", ["col_a"])
    assert rb_drop.is_supported is True
    assert len(rb_drop.rollback_steps) == 3
    assert "RESTORE_DROPPED_COLUMNS" in rb_drop.rollback_steps[1].action

    rb_knn = RollbackPlanBuilder.build_rollback_plan("ImputationTransformation", ["col_a"])
    assert "REVERT_IMPUTED_VALUES" in rb_knn.rollback_steps[1].action


def test_validation_rule_generator():
    """Test ValidationRuleGenerator checklist items."""
    rules = ValidationRuleGenerator.generate_rules("FeatureDropTransformation", ["col_a"])
    assert len(rules) >= 3
    rule_ids = [r.rule_id for r in rules]
    assert "val-col-exists" in rule_ids
    assert "val-no-target-leakage" in rule_ids
    assert "val-non-empty-df" in rule_ids


def test_experiment_validator_failures():
    """Test ExperimentValidator raises ValueError on invalid plan objects."""
    rb = RollbackPlanBuilder.build_rollback_plan("FeatureDropTransformation", ["col_a"])
    builder = (
        ExperimentPlanBuilder()
        .with_plan_id("plan-1")
        .with_hypothesis_id("hyp-1")
        .with_transformation_type("FeatureDropTransformation")
        .with_rollback_plan(rb)
        .with_execution_steps([])  # Empty steps -> invalid!
    )
    with pytest.raises(ValueError, match="ExperimentPlan validation failed"):
        builder.build()


def test_builder_missing_fields_validation():
    """Test ExperimentPlanBuilder raises ValueError when mandatory fields are missing."""
    builder = ExperimentPlanBuilder()
    with pytest.raises(ValueError, match="ExperimentPlan 'plan_id' is required"):
        builder.build()


def test_api_plan_endpoint_with_hypothesis():
    """Test POST /autoscientist/plan with direct hypothesis JSON payload."""
    hyp = _create_test_hypothesis("FeatureDropTransformation")

    response = client.post(
        "/autoscientist/plan",
        json={"hypothesis": hyp.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "experiment_plan" in data
    assert data["experiment_plan"]["hypothesis_id"] == hyp.id
    assert data["experiment_plan"]["transformation_type"] == "FeatureDropTransformation"
    assert len(data["experiment_plan"]["execution_steps"]) > 0


def test_api_plan_endpoint_with_report():
    """Test POST /autoscientist/plan with raw GenomeReportResponse JSON payload."""
    df = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="plan_report_test.csv")

    response = client.post(
        "/autoscientist/plan",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "experiment_plan" in data
    assert data["experiment_plan"]["plan_id"] is not None


def test_api_plan_endpoint_bad_request():
    """Test POST /autoscientist/plan without payload returns HTTP 400."""
    response = client.post("/autoscientist/plan", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, hypothesis, reasoning_trace, or report" in response.json()["detail"]

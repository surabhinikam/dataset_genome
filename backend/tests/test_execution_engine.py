"""
tests/test_execution_engine.py — Unit & Integration tests for Sprint 3.5B Execution Engine.

Tests all transformation plugins, transformation registry, pre/post validation, dataset versioning,
sandboxed execution runner, failure handling, and POST /autoscientist/execute API integration.
"""

from pathlib import Path
from uuid import uuid4
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.execution_builder import ExecutionResultBuilder
from services.autoscientist.execution_engine import ExecutionEngine
from services.autoscientist.execution_models import ExecutionResult, ExecutionStatus
from services.autoscientist.execution_validator import ExecutionValidator
from services.autoscientist.experiment_planner import ExperimentPlanner
from services.autoscientist.hypothesis_builder import ScientificHypothesisBuilder
from services.autoscientist.hypothesis_constants import RiskLevel
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.sandbox_runner import SandboxedExecutionRunner
from services.autoscientist.transformation_registry import TransformationRegistry
from services.autoscientist.transformations import (
    FeatureDropTransformation,
    FeaturePruningTransformation,
    KNNImputationTransformation,
    MedianImputationTransformation,
    SMOTEClassRebalancingTransformation,
    WinsorizationTransformation,
)
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
experiment_planner = ExperimentPlanner()
execution_engine = ExecutionEngine()


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


def test_every_transformation_execution():
    """Test execution of all transformation plugins on DataFrame inputs."""
    # 1. FeatureDropTransformation
    df_drop = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [4, 5, 6]})
    t_drop = FeatureDropTransformation()
    res_df, logs, _ = t_drop.transform(df_drop, {"drop_columns": ["col_b"]}, ["col_b"])
    assert "col_b" not in res_df.columns
    assert "col_a" in res_df.columns

    # 2. KNNImputationTransformation
    df_knn = pd.DataFrame({"a": [1.0, np.nan, 3.0, 4.0, 5.0], "b": [10.0, 20.0, 30.0, 40.0, 50.0]})
    t_knn = KNNImputationTransformation()
    res_knn, logs_knn, _ = t_knn.transform(df_knn, {"n_neighbors": 2}, ["a"])
    assert not res_knn["a"].isna().any()

    # 3. MedianImputationTransformation
    df_med = pd.DataFrame({"a": [10.0, np.nan, 30.0], "b": ["x", None, "x"]})
    t_med = MedianImputationTransformation()
    res_med, _, _ = t_med.transform(df_med, {}, ["a", "b"])
    assert not res_med["a"].isna().any()
    assert not res_med["b"].isna().any()

    # 4. WinsorizationTransformation
    df_win = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 500.0]})
    t_win = WinsorizationTransformation()
    res_win, _, _ = t_win.transform(df_win, {"lower_quantile": 0.01, "upper_quantile": 0.90}, ["val"])
    assert res_win["val"].max() < 500.0

    # 5. SMOTEClassRebalancingTransformation
    df_smote = pd.DataFrame({"feature": list(range(10)), "target": [0] * 8 + [1, 1]})
    t_smote = SMOTEClassRebalancingTransformation()
    res_smote, _, _ = t_smote.transform(df_smote, {}, ["target"])
    assert len(res_smote) >= len(df_smote)

    # 6. FeaturePruningTransformation
    df_prune = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [1.01, 2.01, 3.01]})
    t_prune = FeaturePruningTransformation()
    res_prune, _, _ = t_prune.transform(df_prune, {"retain_column": "col_a", "prune_column": "col_b"}, ["col_b"])
    assert "col_b" not in res_prune.columns


def test_transformation_registry():
    """Test TransformationRegistry plugin lookup and dynamic registration."""
    registry = TransformationRegistry()
    assert registry.has("FeatureDropTransformation")
    assert registry.has("ImputationTransformation")

    t_instance = registry.get("FeatureDropTransformation")
    assert isinstance(t_instance, FeatureDropTransformation)

    with pytest.raises(ValueError, match="Unsupported transformation type"):
        registry.get("InvalidNonExistentTransformation")


def test_pre_and_post_execution_validation():
    """Test ExecutionValidator pre and post execution checks."""
    hyp = _create_test_hypothesis("FeatureDropTransformation", target_col="col_b")
    plan = experiment_planner.create_plan(hyp)

    # Empty DF pre-validation
    with pytest.raises(ValueError, match="Pre-execution validation failed"):
        ExecutionValidator.validate_pre_execution(plan, pd.DataFrame())

    # Empty DF post-validation
    with pytest.raises(ValueError, match="Post-execution validation failed"):
        ExecutionValidator.validate_post_execution(pd.DataFrame({"a": [1]}), pd.DataFrame(), plan)


def test_sandboxed_execution_runner():
    """Test SandboxedExecutionRunner metrics capture and exception handling."""
    df = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [4, 5, 6]})
    t_drop = FeatureDropTransformation()

    sandbox_res = SandboxedExecutionRunner.execute_in_sandbox(
        transformation=t_drop,
        df=df,
        parameters={"drop_columns": ["col_b"]},
        target_columns=["col_b"]
    )

    assert sandbox_res.execution_time_ms >= 0.0
    assert sandbox_res.memory_usage_mb >= 0.0
    assert len(sandbox_res.logs) > 0
    assert len(sandbox_res.errors) == 0


def test_execution_engine_end_to_end():
    """Test ExecutionEngine plan execution and file versioning persistence."""
    df = pd.DataFrame({"facility_code": [999] * 10, "age": [20 + i for i in range(10)]})
    hyp = _create_test_hypothesis("FeatureDropTransformation", target_col="facility_code", params={"drop_columns": ["facility_code"]})
    plan = experiment_planner.create_plan(hyp)

    dataset_id = uuid4()
    result = execution_engine.execute_plan(plan=plan, df=df, dataset_id=dataset_id, source_filename="test_input.csv")

    assert isinstance(result, ExecutionResult)
    assert result.status == ExecutionStatus.COMPLETED
    assert result.dataset_version == "v1.1.0"
    assert result.columns_before == 2
    assert result.columns_after == 1
    assert Path(result.output_dataset_path).exists()


def test_builder_missing_fields_validation():
    """Test ExecutionResultBuilder raises ValueError when mandatory fields are missing."""
    builder = ExecutionResultBuilder()
    with pytest.raises(ValueError, match="ExecutionResult 'execution_id' is required"):
        builder.build()


def test_api_execute_endpoint_with_plan():
    """Test POST /autoscientist/execute with direct experiment_plan payload."""
    hyp = _create_test_hypothesis("FeatureDropTransformation", target_col="facility_code", params={"drop_columns": ["facility_code"]})
    plan = experiment_planner.create_plan(hyp)

    response = client.post(
        "/autoscientist/execute",
        json={"experiment_plan": plan.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "execution_result" in data
    assert data["execution_result"]["status"] == "completed"
    assert data["execution_result"]["plan_id"] == plan.plan_id


def test_api_execute_endpoint_with_report():
    """Test POST /autoscientist/execute with raw GenomeReportResponse JSON payload."""
    df = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="exec_report_test.csv")

    response = client.post(
        "/autoscientist/execute",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "execution_result" in data
    assert data["execution_result"]["status"] == "completed"


def test_api_execute_endpoint_bad_request():
    """Test POST /autoscientist/execute without payload returns HTTP 400."""
    response = client.post("/autoscientist/execute", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, experiment_plan, hypothesis, or report" in response.json()["detail"]

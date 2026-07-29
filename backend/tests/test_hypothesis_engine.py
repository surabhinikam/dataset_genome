"""
tests/test_hypothesis_engine.py — Unit & Integration tests for Sprint 3.4 Scientific Hypothesis Generator.

Tests hypothesis template generation across all 6 categories, parameter factory outputs,
predicted metric delta bounds, confidence bounds, validator failures, builder validation,
and POST /autoscientist/hypothesis API integration.
"""

from uuid import uuid4
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.hypothesis_builder import ScientificHypothesisBuilder
from services.autoscientist.hypothesis_constants import ParameterFactory, RiskLevel
from services.autoscientist.hypothesis_engine import ScientificHypothesisGenerator
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.hypothesis_validator import HypothesisValidator
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()
hypothesis_generator = ScientificHypothesisGenerator()


def _create_test_reasoning_trace(category: ObservationCategory, evidence: dict = None):
    """Helper to build ReasoningTrace for testing."""
    obs = (
        ScientificObservationBuilder()
        .with_id(f"obs-{category.value}")
        .with_category(category)
        .with_title(f"Test Issue {category.value}")
        .with_summary("Test observation summary")
        .with_affected_columns(["col_target"])
        .with_severity(0.85)
        .with_confidence(0.95)
        .with_evidence(evidence or {"column_name": "col_target", "missing_rate": 0.20, "outlier_ratio": 0.08, "majority_class_ratio": 0.90, "pearson_coefficient": 0.92, "column_1": "col_a", "column_2": "col_b", "constant_columns": ["col_target"]})
        .with_recommendations(["Test recommendation"])
        .build()
    )
    queue = ranking_engine.rank_observations([obs])
    context = ReasoningContext(prioritized_problem=queue.ranked_problems[0])
    return reasoning_engine.generate_reasoning_trace(context)


def test_hypothesis_generation_all_categories():
    """Test hypothesis generation for all 6 profiler categories."""
    categories = [
        ObservationCategory.COMPLETENESS,
        ObservationCategory.CORRELATION,
        ObservationCategory.BALANCE,
        ObservationCategory.NOISE,
        ObservationCategory.CONSISTENCY,
        ObservationCategory.FEATURE_QUALITY,
    ]

    for cat in categories:
        trace = _create_test_reasoning_trace(cat)
        hypothesis = hypothesis_generator.generate_hypothesis(trace)

        assert isinstance(hypothesis, ScientificHypothesis)
        assert hypothesis.problem_id == trace.problem_id
        assert len(hypothesis.statement) > 0
        assert len(hypothesis.causal_mechanism) > 0
        assert len(hypothesis.transformation_type) > 0
        assert isinstance(hypothesis.proposed_parameters, dict)
        assert len(hypothesis.proposed_parameters) > 0
        assert 0.001 <= hypothesis.predicted_metric_delta <= 0.200
        assert 0.0 <= hypothesis.estimated_confidence <= 1.0
        assert isinstance(hypothesis.risk_level, RiskLevel)
        assert len(hypothesis.assumptions) > 0
        assert len(hypothesis.constraints) > 0


def test_parameter_factories():
    """Test parameter factory helper functions."""
    knn_params = ParameterFactory.knn_imputation(n_neighbors=7, weights="distance")
    assert knn_params == {"n_neighbors": 7, "weights": "distance"}

    median_params = ParameterFactory.median_imputation()
    assert median_params == {"strategy": "median"}

    smote_params = ParameterFactory.smote(sampling_strategy="auto", k_neighbors=3)
    assert smote_params == {"sampling_strategy": "auto", "k_neighbors": 3}

    drop_params = ParameterFactory.feature_drop(drop_columns=["col1", "col2"])
    assert drop_params == {"drop_columns": ["col1", "col2"]}

    winsor_params = ParameterFactory.winsorization(lower_quantile=0.02, upper_quantile=0.98)
    assert winsor_params == {"lower_quantile": 0.02, "upper_quantile": 0.98}


def test_predicted_metric_delta_and_confidence_bounds():
    """Verify that predicted metric delta is strictly within [0.001, 0.200] and confidence within [0.0, 1.0]."""
    for cat in ObservationCategory:
        trace = _create_test_reasoning_trace(cat)
        hypothesis = hypothesis_generator.generate_hypothesis(trace)
        assert 0.001 <= hypothesis.predicted_metric_delta <= 0.200
        assert 0.0 <= hypothesis.estimated_confidence <= 1.0


def test_validator_failures():
    """Test HypothesisValidator raises ValueError on invalid fields or bounds."""
    # Metric delta out of bounds (< 0.001)
    builder = (
        ScientificHypothesisBuilder()
        .with_id("hyp-1")
        .with_problem_id("prob-1")
        .with_statement("Statement claim")
        .with_causal_mechanism("Mechanism")
        .with_transformation_type("FeatureDropTransformation")
        .with_proposed_parameters({"drop_columns": ["col_a"]})
        .with_predicted_metric_delta(0.00001)  # Invalid!
        .with_estimated_confidence(0.9)
        .with_risk_level(RiskLevel.LOW)
        .with_assumptions(["a1"])
        .with_constraints(["c1"])
    )
    with pytest.raises(ValueError):
        builder.build()


def test_builder_missing_fields_validation():
    """Test ScientificHypothesisBuilder raises ValueError when mandatory fields are omitted."""
    builder = ScientificHypothesisBuilder()
    with pytest.raises(ValueError, match="ScientificHypothesis 'id' is required"):
        builder.build()


def test_api_hypothesis_endpoint_with_trace():
    """Test POST /autoscientist/hypothesis with reasoning_trace payload."""
    trace = _create_test_reasoning_trace(ObservationCategory.FEATURE_QUALITY)

    response = client.post(
        "/autoscientist/hypothesis",
        json={"reasoning_trace": trace.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "hypothesis" in data
    assert data["hypothesis"]["transformation_type"] == "FeatureDropTransformation"
    assert 0.001 <= data["hypothesis"]["predicted_metric_delta"] <= 0.200


def test_api_hypothesis_endpoint_with_report():
    """Test POST /autoscientist/hypothesis with raw GenomeReportResponse payload."""
    df = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="hyp_report_test.csv")

    response = client.post(
        "/autoscientist/hypothesis",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "hypothesis" in data
    assert data["hypothesis"]["problem_id"] is not None


def test_api_hypothesis_endpoint_bad_request():
    """Test POST /autoscientist/hypothesis without payload returns HTTP 400."""
    response = client.post("/autoscientist/hypothesis", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, reasoning_trace payload, or report" in response.json()["detail"]

"""
tests/test_reasoning_engine.py — Unit & Integration tests for Sprint 3.3 Reasoning Engine.

Tests template selection for all 6 categories, decision branching (imputation vs drop),
trace validation, memory interface stubs, and POST /autoscientist/reason API integration.
"""

from uuid import uuid4
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.reasoning_builder import ReasoningTraceBuilder
from services.autoscientist.reasoning_context import ReasoningContext
from services.autoscientist.reasoning_engine import ReasoningEngine
from services.autoscientist.reasoning_models import ReasoningTrace, ScientificMemoryInterface
from services.autoscientist.reasoning_validator import ReasoningValidator
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
ranking_engine = ProblemRankingEngine()
reasoning_engine = ReasoningEngine()


def _create_ranked_problem(
    obs_id: str,
    category: ObservationCategory,
    title: str,
    severity: float,
    evidence: dict = None,
    affected_cols: list = None
):
    """Helper to create RankedProblem for testing."""
    builder = (
        ScientificObservationBuilder()
        .with_id(obs_id)
        .with_category(category)
        .with_title(title)
        .with_summary(f"Test summary for {title}")
        .with_affected_columns(affected_cols or ["col_a"])
        .with_severity(severity)
        .with_confidence(0.95)
        .with_evidence(evidence or {"test_key": "test_val"})
        .with_recommendations(["Test recommendation"])
    )
    obs = builder.build()
    queue = ranking_engine.rank_observations([obs])
    return queue.ranked_problems[0]


def test_valid_context_reasoning_all_categories():
    """Test reasoning generation for all 6 profiler categories."""
    categories = [
        ObservationCategory.COMPLETENESS,
        ObservationCategory.CORRELATION,
        ObservationCategory.BALANCE,
        ObservationCategory.NOISE,
        ObservationCategory.CONSISTENCY,
        ObservationCategory.FEATURE_QUALITY,
    ]

    for cat in categories:
        problem = _create_ranked_problem(f"obs-{cat.value}", cat, f"Title {cat.value}", 0.8)
        context = ReasoningContext(prioritized_problem=problem)
        trace = reasoning_engine.generate_reasoning_trace(context)

        assert isinstance(trace, ReasoningTrace)
        assert trace.category == cat
        assert len(trace.reasoning_summary) > 0
        assert len(trace.inferred_mechanism) > 0
        assert len(trace.recommended_transformation_class) > 0
        assert 0.0 <= trace.confidence <= 1.0
        assert len(trace.assumptions) > 0
        assert len(trace.constraints) > 0
        assert len(trace.risks) > 0


def test_completeness_imputation_vs_drop_branching():
    """Test completeness template branching: >50% missing -> FeatureDrop, <=50% missing -> Imputation."""
    # 1. Moderate missingness (30%) -> ImputationTransformation
    problem_moderate = _create_ranked_problem(
        "obs-mod-miss",
        ObservationCategory.COMPLETENESS,
        "Moderate Missingness",
        0.5,
        evidence={"missing_rate": 0.30}
    )
    trace_mod = reasoning_engine.generate_reasoning_trace(ReasoningContext(prioritized_problem=problem_moderate))
    assert trace_mod.recommended_transformation_class == "ImputationTransformation"
    assert "KNN or median/mode" in trace_mod.reasoning_summary

    # 2. Severe missingness (70%) -> FeatureDropTransformation
    problem_severe = _create_ranked_problem(
        "obs-sev-miss",
        ObservationCategory.COMPLETENESS,
        "Severe Missingness",
        0.9,
        evidence={"missing_rate": 0.70}
    )
    trace_sev = reasoning_engine.generate_reasoning_trace(ReasoningContext(prioritized_problem=problem_severe))
    assert trace_sev.recommended_transformation_class == "FeatureDropTransformation"
    assert "Dropping column(s)" in trace_sev.reasoning_summary


def test_consistency_dups_vs_mixed_types_branching():
    """Test consistency template branching: duplicates vs mixed types."""
    # Duplicates -> RowDeduplicationTransformation
    prob_dups = _create_ranked_problem(
        "obs-dups",
        ObservationCategory.CONSISTENCY,
        "Duplicate Rows Detected",
        0.6,
        evidence={"duplicate_rows": 50, "duplicate_ratio": 0.05}
    )
    trace_dups = reasoning_engine.generate_reasoning_trace(ReasoningContext(prioritized_problem=prob_dups))
    assert trace_dups.recommended_transformation_class == "RowDeduplicationTransformation"

    # Mixed Types -> TypeUnificationTransformation
    prob_mixed = _create_ranked_problem(
        "obs-mixed",
        ObservationCategory.CONSISTENCY,
        "Mixed Data Types in Column",
        0.7,
        evidence={"type_uniformity_score": 0.40}
    )
    trace_mixed = reasoning_engine.generate_reasoning_trace(ReasoningContext(prioritized_problem=prob_mixed))
    assert trace_mixed.recommended_transformation_class == "TypeUnificationTransformation"


def test_validator_failure_malformed_traces():
    """Test ReasoningValidator raises ValueError on incomplete or invalid fields."""
    # Missing reasoning_summary
    builder = (
        ReasoningTraceBuilder()
        .with_id("t-1")
        .with_problem_id("p-1")
        .with_category(ObservationCategory.NOISE)
        .with_inferred_mechanism("mechanism")
        .with_recommended_transformation_class("WinsorizationTransformation")
        .with_assumptions(["a1"])
        .with_constraints(["c1"])
        .with_risks(["r1"])
    )
    with pytest.raises(ValueError, match="ReasoningTrace validation failed"):
        builder.build()


def test_memory_interface_stub_integration():
    """Test memory interface stub integration in ReasoningContext."""
    prob = _create_ranked_problem("obs-mem", ObservationCategory.CORRELATION, "Collinear", 0.9)
    memory_stub = ScientificMemoryInterface(
        memory_enabled=True,
        similar_past_experiments_count=5,
        historical_success_rate=0.85,
        recommended_recipes=["Prune feature 'col_b'"]
    )
    context = ReasoningContext(prioritized_problem=prob, memory_interface=memory_stub)
    trace = reasoning_engine.generate_reasoning_trace(context)

    assert trace.memory_insights is not None
    assert trace.memory_insights.memory_enabled is True
    assert trace.memory_insights.similar_past_experiments_count == 5
    assert trace.memory_insights.historical_success_rate == 0.85


def test_api_reason_endpoint_with_problem():
    """Test POST /autoscientist/reason with ranked_problem JSON payload."""
    prob = _create_ranked_problem("obs-api-r1", ObservationCategory.FEATURE_QUALITY, "Constant Feature", 1.0)

    response = client.post(
        "/autoscientist/reason",
        json={"ranked_problem": prob.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "reasoning_trace" in data
    assert data["problem_id"] == "obs-api-r1"
    assert data["reasoning_trace"]["recommended_transformation_class"] == "FeatureDropTransformation"


def test_api_reason_endpoint_with_report():
    """Test POST /autoscientist/reason with raw GenomeReportResponse payload."""
    df = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="reason_report_test.csv")

    response = client.post(
        "/autoscientist/reason",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "reasoning_trace" in data
    assert data["reasoning_trace"]["category"] in ["feature_quality", "completeness", "consistency", "balance", "noise", "correlation"]


def test_api_reason_endpoint_bad_request():
    """Test POST /autoscientist/reason without payload returns HTTP 400."""
    response = client.post("/autoscientist/reason", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, ranked_problem payload, or report" in response.json()["detail"]

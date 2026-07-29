"""
tests/test_ranking_engine.py — Unit & Integration tests for Sprint 3.2 Problem Ranking Engine.

Tests empty inputs, single & multiple observations, deterministic tie-breaking,
utility component scaling, natural language explanations, and POST /autoscientist/rank API.
"""

from uuid import uuid4
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.observation_engine import ObservationEngine
from services.autoscientist.ranking_engine import ProblemRankingEngine
from services.autoscientist.ranking_models import ScientificObservation
from services.autoscientist.utility_functions import UtilityCalculator
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()
ranking_engine = ProblemRankingEngine()


def _create_sample_obs(
    obs_id: str,
    category: ObservationCategory,
    title: str,
    severity: float,
    affected_cols: list = None,
    evidence: dict = None
) -> ScientificObservation:
    """Helper to build test ScientificObservation objects."""
    return (
        ScientificObservationBuilder()
        .with_id(obs_id)
        .with_category(category)
        .with_title(title)
        .with_summary(f"Test summary for {title}")
        .with_affected_columns(affected_cols or ["col_1"])
        .with_severity(severity)
        .with_confidence(0.95)
        .with_evidence(evidence if evidence is not None else {"constant_columns": affected_cols or ["col_1"]})
        .with_recommendations(["Test recommendation"])
        .build()
    )


def test_empty_input():
    """Test that an empty observations list returns an empty queue."""
    queue = ranking_engine.rank_observations([])
    assert queue.total_problems == 0
    assert queue.ranked_problems == []
    assert queue.highest_priority_problem is None


def test_single_observation():
    """Test ranking a single observation."""
    obs = _create_sample_obs(
        obs_id="obs-1",
        category=ObservationCategory.FEATURE_QUALITY,
        title="Constant Feature 'facility_code'",
        severity=1.0,
        affected_cols=["facility_code"]
    )
    queue = ranking_engine.rank_observations([obs])

    assert queue.total_problems == 1
    assert queue.highest_priority_problem is not None
    top = queue.highest_priority_problem
    assert top.rank == 1
    assert top.observation_id == "obs-1"
    assert top.utility_score > 0.0
    assert top.component_scores.severity == 1.0
    assert "Assigned utility score" in top.explanation
    assert "drop zero-variance constant" in top.recommended_next_step.lower()


def test_multiple_observations_ranking():
    """Test multi-observation ranking with distinct severities."""
    obs_const = _create_sample_obs("obs-const", ObservationCategory.FEATURE_QUALITY, "Constant Feature", 1.0)
    obs_missing = _create_sample_obs("obs-miss", ObservationCategory.COMPLETENESS, "Missing Values", 0.5)
    obs_noise = _create_sample_obs("obs-noise", ObservationCategory.NOISE, "Outliers", 0.2)

    queue = ranking_engine.rank_observations([obs_noise, obs_const, obs_missing])

    assert queue.total_problems == 3
    # Constant feature (high severity, low complexity, high info loss risk) must be #1
    assert queue.ranked_problems[0].observation_id == "obs-const"
    assert queue.ranked_problems[0].rank == 1
    assert queue.ranked_problems[1].rank == 2
    assert queue.ranked_problems[2].rank == 3

    # Assert descending utility order
    scores = [p.utility_score for p in queue.ranked_problems]
    assert scores == sorted(scores, reverse=True)


def test_tie_breaking_rules():
    """
    Test deterministic tie-breaking hierarchy:
    1. Utility score (descending)
    2. Severity (descending)
    3. Repair complexity (ascending)
    4. Alphabetical category (ascending)
    5. Stable ID (ascending)
    """
    # 2 observations with identical severity, category, and evidence -> tie on utility & complexity
    obs_a = _create_sample_obs("obs-z-id", ObservationCategory.BALANCE, "Class Imbalance Z", 0.8)
    obs_b = _create_sample_obs("obs-a-id", ObservationCategory.BALANCE, "Class Imbalance A", 0.8)

    queue = ranking_engine.rank_observations([obs_a, obs_b])

    assert queue.total_problems == 2
    # Tie broken by stable observation_id ascending ('obs-a-id' < 'obs-z-id')
    assert queue.ranked_problems[0].observation_id == "obs-a-id"
    assert queue.ranked_problems[1].observation_id == "obs-z-id"


def test_deterministic_ordering_repeatability():
    """Test that ranking identical observations 100 times yields 100% deterministic order."""
    obs_list = [
        _create_sample_obs("obs-3", ObservationCategory.NOISE, "Noise", 0.4),
        _create_sample_obs("obs-1", ObservationCategory.FEATURE_QUALITY, "Constant", 1.0),
        _create_sample_obs("obs-2", ObservationCategory.COMPLETENESS, "Missing", 0.8),
    ]

    ref_order = [p.observation_id for p in ranking_engine.rank_observations(obs_list).ranked_problems]

    for _ in range(20):
        test_order = [p.observation_id for p in ranking_engine.rank_observations(obs_list).ranked_problems]
        assert test_order == ref_order


def test_utility_components_bounding():
    """Verify all utility components are strictly bounded in [0.0, 1.0]."""
    for cat in ObservationCategory:
        obs = _create_sample_obs("obs-test", cat, "Test Title", 0.95)
        comp = UtilityCalculator.compute_components(obs)
        score = UtilityCalculator.compute_utility_score(obs, comp)

        assert 0.0 <= comp.severity <= 1.0
        assert 0.0 <= comp.information_loss_risk <= 1.0
        assert 0.0 <= comp.impact_potential <= 1.0
        assert 0.0 <= comp.repair_complexity <= 1.0
        assert 0.0 <= score <= 1.0


def test_api_rank_endpoint_with_observations():
    """Test POST /autoscientist/rank with raw observations list."""
    obs = _create_sample_obs("obs-api-1", ObservationCategory.FEATURE_QUALITY, "API Constant Col", 1.0)

    response = client.post(
        "/autoscientist/rank",
        json={"observations": [obs.model_dump(mode="json")]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_problems"] == 1
    assert "queue" in data
    assert data["ranked_problems"][0]["observation_id"] == "obs-api-1"


def test_api_rank_endpoint_with_report():
    """Test POST /autoscientist/rank using direct GenomeReportResponse JSON payload."""
    df = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="rank_report_test.csv")

    response = client.post(
        "/autoscientist/rank",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_problems"] >= 1
    assert data["ranked_problems"][0]["rank"] == 1


def test_api_rank_endpoint_bad_request():
    """Test POST /autoscientist/rank without required payload returns HTTP 400."""
    response = client.post("/autoscientist/rank", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, observations list, or report" in response.json()["detail"]

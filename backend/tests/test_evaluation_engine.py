"""
tests/test_evaluation_engine.py — Unit & Integration tests for Sprint 3.6 Evaluation Engine.

Tests metric collection, metric comparison deltas, prediction errors, confidence calibration,
hypothesis verification (VERIFIED, PARTIALLY_VERIFIED, FAILED), recommendations, validator, builder,
and POST /autoscientist/evaluate API integration.
"""

from uuid import uuid4
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.intelligence import GenomeReportResponse
from services.autoscientist.comparison_engine import ComparisonEngine
from services.autoscientist.evaluation_builder import EvaluationReportBuilder
from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_engine import EvaluationEngine
from services.autoscientist.evaluation_models import EvaluationReport, MetricDelta
from services.autoscientist.evaluation_validator import EvaluationValidator
from services.autoscientist.hypothesis_verifier import HypothesisVerifier
from services.autoscientist.metric_collector import MetricCollector
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
evaluation_engine = EvaluationEngine()


def _create_sample_reports():
    """Helper to generate baseline and improved GenomeReportResponse objects."""
    df_base = pd.DataFrame({
        "facility_code": [999] * 15,
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })
    df_improved = pd.DataFrame({
        "patient_id": [f"ID_{i}" for i in range(15)],
        "age": [20 + i for i in range(15)]
    })

    dataset_id = uuid4()
    rep_base = intelligence_engine.analyze_dataframe(df_base, dataset_id, filename="baseline.csv")
    rep_imp = intelligence_engine.analyze_dataframe(df_improved, dataset_id, filename="transformed.csv")
    return rep_base, rep_imp


def test_metric_collector():
    """Test MetricCollector extracts quality metric dictionary."""
    rep_base, _ = _create_sample_reports()
    metrics = MetricCollector.collect_metrics(rep_base)

    assert "health_score" in metrics
    assert "quality_score" in metrics
    assert "completeness_score" in metrics
    assert "missing_rate" in metrics
    assert 0.0 <= metrics["quality_score"] <= 1.0


def test_comparison_engine():
    """Test ComparisonEngine metric deltas computation."""
    m_before = {"health_score": 70.0, "missing_rate": 0.20}
    m_after = {"health_score": 85.0, "missing_rate": 0.05}

    deltas = ComparisonEngine.compare_metrics(m_before, m_after)
    assert len(deltas) == 2

    d_health = next(d for d in deltas if d.metric_name == "health_score")
    assert d_health.absolute_delta == 15.0
    assert d_health.improved is True

    d_missing = next(d for d in deltas if d.metric_name == "missing_rate")
    assert d_missing.absolute_delta == -0.15
    assert d_missing.improved is True


def test_hypothesis_verifier_outcomes():
    """Test HypothesisVerifier VERIFIED, PARTIALLY_VERIFIED, and FAILED outcomes."""
    # 1. VERIFIED (actual >= 70% of predicted)
    out_v, err_v, rec_v, cal_v = HypothesisVerifier.verify_hypothesis(predicted_improvement=0.05, actual_improvement=0.05)
    assert out_v == EvaluationOutcome.VERIFIED
    assert rec_v == EvaluationRecommendation.STORE_EXPERIMENT
    assert cal_v > 0.0

    # 2. PARTIALLY_VERIFIED (actual >= 30% of predicted)
    out_p, err_p, rec_p, cal_p = HypothesisVerifier.verify_hypothesis(predicted_improvement=0.10, actual_improvement=0.04)
    assert out_p == EvaluationOutcome.PARTIALLY_VERIFIED
    assert rec_p == EvaluationRecommendation.RETRY_WITH_DIFFERENT_PARAMETERS

    # 3. FAILED (actual <= 0.0)
    out_f, err_f, rec_f, cal_f = HypothesisVerifier.verify_hypothesis(predicted_improvement=0.05, actual_improvement=-0.02)
    assert out_f == EvaluationOutcome.FAILED
    assert rec_f == EvaluationRecommendation.REJECT_HYPOTHESIS
    assert cal_f < 0.0


def test_evaluation_validator_checks():
    """Test EvaluationValidator input and output validations."""
    rep_base, rep_imp = _create_sample_reports()
    assert EvaluationValidator.validate_inputs(rep_base, rep_imp) is True

    builder = (
        EvaluationReportBuilder()
        .with_evaluation_id("eval-1")
        .with_experiment_id("exp-1")
        .with_health_scores(150.0, 80.0)  # Invalid health score > 100
    )
    with pytest.raises(ValueError):
        builder.build()


def test_evaluation_engine_end_to_end():
    """Test EvaluationEngine full evaluation workflow."""
    rep_base, rep_imp = _create_sample_reports()
    report = evaluation_engine.evaluate_experiment(original_report=rep_base, transformed_report=rep_imp)

    assert isinstance(report, EvaluationReport)
    assert report.evaluation_id.startswith("eval-")
    assert len(report.metric_deltas) > 0
    assert report.health_score_before <= report.health_score_after


def test_api_evaluate_endpoint_with_reports():
    """Test POST /autoscientist/evaluate with direct reports payload."""
    rep_base, rep_imp = _create_sample_reports()

    response = client.post(
        "/autoscientist/evaluate",
        json={
            "original_report": rep_base.model_dump(mode="json"),
            "transformed_report": rep_imp.model_dump(mode="json")
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "evaluation_report" in data
    assert data["evaluation_report"]["overall_result"] in ["VERIFIED", "PARTIALLY_VERIFIED", "FAILED"]


def test_api_evaluate_endpoint_bad_request():
    """Test POST /autoscientist/evaluate without payload returns HTTP 400."""
    response = client.post("/autoscientist/evaluate", json={})
    assert response.status_code == 400
    assert "Must provide dataset_id, or original_report and transformed_report" in response.json()["detail"]

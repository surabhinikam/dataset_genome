"""
tests/test_observation_engine.py — Unit & Integration tests for Sprint 3.1 Observation Engine.

Tests all profiler observation mapping categories (Completeness, Consistency, Balance,
Correlation, Noise, Feature Quality), severity calibration, evidence payloads,
healthy dataset fallback, and POST /autoscientist/observe API endpoint.
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
from services.autoscientist.severity_engine import SeverityEngine
from services.dataset_intelligence.engine import DatasetIntelligenceEngine

client = TestClient(app)
intelligence_engine = DatasetIntelligenceEngine()
observation_engine = ObservationEngine()


def test_healthy_dataset_observation():
    """Test that a clean, healthy dataset with 0 anomalies emits optimal observation."""
    # Data with low pairwise correlation r < 0.85 and no constant/id/missing/outlier flaws
    df = pd.DataFrame({
        "age": [20, 50, 25, 60, 30, 45, 40, 35, 55, 65],
        "category": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        "score": [10.0, 90.0, 50.0, 20.0, 80.0, 30.0, 70.0, 40.0, 60.0, 15.0]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="clean.csv")

    observations = observation_engine.process_report(report)

    assert len(observations) == 1
    obs = observations[0]
    assert obs.severity == 0.0
    assert obs.confidence == 0.95
    assert obs.metadata.get("is_statistically_optimal") is True
    assert "Statistically Optimal" in obs.title


def test_missing_values_observation():
    """Test completeness profiler mapping for dataset-wide and column missingness."""
    df = pd.DataFrame({
        "reg_time": [None] * 8 + [1.0, 2.0],  # 80% missing -> severe column missingness
        "wait_time": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="missing.csv")

    observations = observation_engine.process_report(report)

    completeness_obs = [o for o in observations if o.category == ObservationCategory.COMPLETENESS]
    assert len(completeness_obs) >= 1

    col_obs = [o for o in completeness_obs if o.id.startswith("obs-comp-col-")]
    assert len(col_obs) == 1
    assert col_obs[0].severity > 0.5
    assert col_obs[0].evidence["missing_rate"] == 0.8
    assert col_obs[0].evidence["missing_row_count"] == 8


def test_imbalance_observation():
    """Test balance profiler mapping when majority class ratio >= 85%."""
    df = pd.DataFrame({
        "target": ["Class_A"] * 9 + ["Class_B"],  # 90% majority ratio
        "feature": list(range(10))
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="imbalanced.csv")

    observations = observation_engine.process_report(report)

    balance_obs = [o for o in observations if o.category == ObservationCategory.BALANCE]
    assert len(balance_obs) == 1
    assert balance_obs[0].affected_columns == ["target"]
    assert balance_obs[0].severity > 0.0
    assert balance_obs[0].evidence["majority_class_ratio"] == 0.9


def test_outliers_observation():
    """Test noise profiler mapping for IQR column outliers."""
    # 20 normal values around 50, plus 3 extreme outliers (500, 600, 700)
    data = [50.0 + i for i in range(20)] + [500.0, 600.0, 700.0]
    df = pd.DataFrame({"value": data})
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="outliers.csv")

    observations = observation_engine.process_report(report)

    noise_obs = [o for o in observations if o.category == ObservationCategory.NOISE]
    assert len(noise_obs) == 1
    assert noise_obs[0].affected_columns == ["value"]
    assert noise_obs[0].evidence["outlier_count"] >= 3
    assert noise_obs[0].evidence["outlier_ratio"] > 0.03


def test_constant_features_observation():
    """Test feature quality mapper for zero-variance constant columns and ID-like features."""
    n_rows = 15
    df = pd.DataFrame({
        "facility_code": [999] * n_rows,  # Zero variance
        "patient_id": [f"ID_{i}" for i in range(n_rows)],  # 100% unique string IDs (> 10 rows)
        "age": [20 + i for i in range(n_rows)]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="constant.csv")

    observations = observation_engine.process_report(report)

    fq_obs = [o for o in observations if o.category == ObservationCategory.FEATURE_QUALITY]
    assert len(fq_obs) == 2  # 1 constant column obs + 1 ID-like column obs

    const_obs = [o for o in fq_obs if "facility_code" in o.affected_columns][0]
    assert const_obs.severity == 1.0
    assert const_obs.evidence["constant_columns"] == ["facility_code"]


def test_multicollinearity_observation():
    """Test correlation profiler mapping for feature pairs with |r| >= 0.85."""
    df = pd.DataFrame({
        "col_a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "col_b": [1.01, 2.02, 3.01, 4.02, 5.01, 6.02, 7.01, 8.02, 9.01, 10.02]  # r ~ 0.999
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="collinear.csv")

    observations = observation_engine.process_report(report)

    corr_obs = [o for o in observations if o.category == ObservationCategory.CORRELATION]
    assert len(corr_obs) == 1
    assert set(corr_obs[0].affected_columns) == {"col_a", "col_b"}
    assert corr_obs[0].severity > 0.8
    assert corr_obs[0].evidence["pearson_coefficient"] > 0.95


def test_mixed_types_and_duplicates_observation():
    """Test consistency profiler mapping for duplicate rows and mixed types."""
    df = pd.DataFrame({
        "col_mixed": [10, "string_val", 20, "string_val_2", 30],
        "col_dup": [1, 1, 1, 1, 1]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="consistency.csv")

    observations = observation_engine.process_report(report)

    cons_obs = [o for o in observations if o.category == ObservationCategory.CONSISTENCY]
    assert len(cons_obs) >= 1


def test_severity_engine_calculations():
    """Test math bounding logic in SeverityEngine."""
    assert SeverityEngine.calculate_completeness_cell_severity(0.02) == 0.0
    assert SeverityEngine.calculate_completeness_cell_severity(0.50) == 1.0
    assert SeverityEngine.calculate_column_missing_severity(0.05) == 0.0
    assert SeverityEngine.calculate_column_missing_severity(0.80) == 1.0
    assert SeverityEngine.calculate_duplicate_rows_severity(0.005) == 0.0
    assert SeverityEngine.calculate_duplicate_rows_severity(0.20) == 1.0
    assert SeverityEngine.calculate_correlation_severity(0.80) == 0.0
    assert SeverityEngine.calculate_correlation_severity(1.0) == 1.0
    assert SeverityEngine.calculate_constant_column_severity() == 1.0


def test_observation_builder_validation():
    """Test error handling in ScientificObservationBuilder when fields are missing."""
    builder = ScientificObservationBuilder()
    with pytest.raises(ValueError, match="Observation 'id' is required"):
        builder.build()

    builder.with_id("test-id")
    with pytest.raises(ValueError, match="Observation 'category' is required"):
        builder.build()


def test_api_observe_endpoint_with_report():
    """Test POST /autoscientist/observe using direct report JSON payload."""
    df = pd.DataFrame({
        "a": [1, None, None, None, 5],
        "b": ["x", "y", "z", "w", "v"]
    })
    dataset_id = uuid4()
    report = intelligence_engine.analyze_dataframe(df, dataset_id, filename="api_test.csv")

    response = client.post(
        "/autoscientist/observe",
        json={"report": report.model_dump(mode="json")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == str(dataset_id)
    assert data["total_observations"] >= 1
    assert "observations" in data
    assert data["observations"][0]["category"] == "completeness"

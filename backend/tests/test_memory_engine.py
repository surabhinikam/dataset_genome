"""
tests/test_memory_engine.py — Unit & Integration tests for Sprint 3.7 Scientific Memory Engine.

Tests experiment encoding, feature vectors, local persistence, vector similarity metrics,
historical retrieval, success statistics, recipe recommendations, and REST API endpoints.
Targeting >95% code coverage.
"""

from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from main import app
from services.autoscientist.evaluation_builder import EvaluationReportBuilder
from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport, MetricDelta
from services.autoscientist.memory_builder import MemoryRecordBuilder
from services.autoscientist.memory_constants import FEATURE_VECTOR_DIMENSION, SimilarityMetric
from services.autoscientist.memory_encoder import MemoryEncoder
from services.autoscientist.memory_engine import ScientificMemoryEngine
from services.autoscientist.memory_models import MemoryRecord, MemorySearchRequest, MemoryStoreRequest
from services.autoscientist.memory_similarity import (
    CosineSimilarityEngine,
    EuclideanSimilarityEngine,
    SimilarityEngineFactory,
)
from services.autoscientist.memory_store import LocalMemoryStore
from services.autoscientist.memory_validator import MemoryValidator

client = TestClient(app)


def _create_sample_evaluation_report(
    eval_id: str = "eval-test-1",
    experiment_id: str = "plan-test-1",
    outcome: EvaluationOutcome = EvaluationOutcome.VERIFIED,
    predicted_imp: float = 0.05,
    actual_imp: float = 0.045,
    health_before: float = 80.0,
    health_after: float = 84.5,
    rec: EvaluationRecommendation = EvaluationRecommendation.STORE_EXPERIMENT,
) -> EvaluationReport:
    """Helper to build test EvaluationReport objects."""
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
        .with_evaluation_id(eval_id)
        .with_experiment_id(experiment_id)
        .with_overall_result(outcome)
        .with_predicted_improvement(predicted_imp)
        .with_actual_improvement(actual_imp)
        .with_prediction_error(abs(predicted_imp - actual_imp))
        .with_metric_deltas([delta])
        .with_health_scores(health_before, health_after)
        .with_recommendation(rec)
        .with_confidence_calibration(0.02)
        .with_metadata({"transformation_type": "KNNImputationTransformation"})
        .build()
    )


def test_memory_builder_and_validations():
    """Test MemoryRecordBuilder and MemoryValidator mandatory field checks."""
    builder = MemoryRecordBuilder()

    # Missing mandatory experiment_id
    with pytest.raises(ValueError, match="experiment_id"):
        builder.build()

    builder.with_experiment_id("exp-1")
    with pytest.raises(ValueError, match="transformation_type"):
        builder.build()

    builder.with_transformation_type("KNNImputationTransformation")
    with pytest.raises(ValueError, match="health scores"):
        builder.build()

    builder.with_health_scores(75.0, 85.0)
    with pytest.raises(ValueError, match="improvements"):
        builder.build()

    builder.with_improvements(0.10, 0.10, 0.0)
    record = builder.build()

    assert record.record_id.startswith("mem-")
    assert record.experiment_id == "exp-1"
    assert record.overall_result == EvaluationOutcome.FAILED

    # Test Validator
    MemoryValidator.validate_record(record)

    # Invalid feature vector length
    record.feature_vector = [0.1, 0.2]
    with pytest.raises(ValueError, match="dimension mismatch"):
        MemoryValidator.validate_record(record)


def test_memory_encoder():
    """Test MemoryEncoder feature vector extraction and MemoryRecord creation."""
    report = _create_sample_evaluation_report()
    vector = MemoryEncoder.encode_feature_vector(report)

    assert len(vector) == FEATURE_VECTOR_DIMENSION
    assert vector[0] == 0.80  # 80.0 / 100
    assert vector[1] == 0.845  # 84.5 / 100
    assert vector[6] == 1.0  # verified
    assert vector[7] == 1.0  # PROCEED recommendation weight

    record = MemoryEncoder.create_memory_record(
        report=report,
        dataset_id=uuid4(),
        transformation_type="KNNImputationTransformation",
        category="completeness",
    )

    assert record.record_id == f"mem-{report.evaluation_id}"
    assert record.transformation_type == "KNNImputationTransformation"
    assert len(record.feature_vector) == FEATURE_VECTOR_DIMENSION


def test_similarity_engines():
    """Test Cosine and Euclidean similarity engines and factory."""
    cosine_engine = CosineSimilarityEngine()
    euclidean_engine = EuclideanSimilarityEngine()

    v1 = [1.0, 0.0, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0]
    v2 = [1.0, 0.0, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0]
    v3 = [0.0, 1.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0]

    # Identical vectors should yield high similarity
    assert cosine_engine.calculate_similarity(v1, v2) == 1.0
    assert euclidean_engine.calculate_similarity(v1, v2) == 1.0

    # Orthogonal / different vectors
    sim_diff = cosine_engine.calculate_similarity(v1, v3)
    assert 0.0 <= sim_diff <= 1.0

    # Ranking helper
    candidates = [("rec-1", v1), ("rec-2", v3)]
    ranked = cosine_engine.rank_similar_vectors(v1, candidates, top_k=2)
    assert len(ranked) == 2
    assert ranked[0][0] == "rec-1"
    assert ranked[0][1] == 1.0

    # Factory lookup
    engine_cos = SimilarityEngineFactory.get_engine(SimilarityMetric.COSINE)
    engine_euc = SimilarityEngineFactory.get_engine(SimilarityMetric.EUCLIDEAN)
    assert isinstance(engine_cos, CosineSimilarityEngine)
    assert isinstance(engine_euc, EuclideanSimilarityEngine)


def test_local_memory_store(tmp_path):
    """Test LocalMemoryStore persistence and querying."""
    store_file = tmp_path / "test_memory.json"
    store = LocalMemoryStore(storage_path=store_file)

    report = _create_sample_evaluation_report(eval_id="eval-store-1")
    record = MemoryEncoder.create_memory_record(report=report, category="completeness")

    store.save_record(record)
    assert store.get_record("mem-eval-store-1") is not None

    records = store.list_records(category="completeness")
    assert len(records) == 1

    # Reload store from disk
    new_store_instance = LocalMemoryStore(storage_path=store_file)
    assert new_store_instance.get_record("mem-eval-store-1") is not None

    # Clear store
    store.clear()
    assert len(store.list_records()) == 0


def test_scientific_memory_engine_end_to_end(tmp_path):
    """Test ScientificMemoryEngine storing, similarity search, stats, and recommendations."""
    store_file = tmp_path / "engine_memory.json"
    store = LocalMemoryStore(storage_path=store_file)
    engine = ScientificMemoryEngine(store=store)

    # 1. Store several evaluation reports
    r1 = _create_sample_evaluation_report(eval_id="e1", experiment_id="p1", outcome=EvaluationOutcome.VERIFIED, actual_imp=0.08)
    r2 = _create_sample_evaluation_report(eval_id="e2", experiment_id="p2", outcome=EvaluationOutcome.FAILED, actual_imp=-0.02, rec=EvaluationRecommendation.REJECT_HYPOTHESIS)

    rec1 = engine.store_evaluation_report(r1, transformation_type="KNNImputationTransformation", category="completeness")
    rec2 = engine.store_evaluation_report(r2, transformation_type="KNNImputationTransformation", category="completeness")

    assert rec1.record_id == "mem-e1"
    assert engine.get_memory_record("mem-e1") is not None

    # 2. Search similar experiments
    search_req = MemorySearchRequest(category="completeness", top_k=5, metric=SimilarityMetric.COSINE)
    retrieval = engine.search_similar_experiments(search_req)

    assert len(retrieval.similar_records) == 2
    assert retrieval.historical_success_rate >= 0.0

    # 3. Get transformation stats
    stats = engine.get_transformation_stats("KNNImputationTransformation")
    assert stats["total_experiments"] == 2
    assert stats["verified_count"] == 1
    assert stats["failed_count"] == 1

    # 4. Generate recipe recommendations
    recipes = engine.generate_recipe_recommendations("completeness")
    assert "category" in recipes
    assert len(recipes["recommended_recipes"]) > 0


def test_api_memory_endpoints(tmp_path):
    """Test REST API memory routes POST /store, POST /search, and GET /{id}."""
    # Test POST /autoscientist/memory/store
    report = _create_sample_evaluation_report(eval_id="eval-api-1")

    res_store = client.post(
        "/autoscientist/memory/store",
        json={"evaluation_report": report.model_dump(mode="json")}
    )
    assert res_store.status_code == 200
    data_store = res_store.json()
    record_id = data_store["record_id"]
    assert record_id == "mem-eval-api-1"

    # Test GET /autoscientist/memory/{id}
    res_get = client.get(f"/autoscientist/memory/{record_id}")
    assert res_get.status_code == 200
    assert res_get.json()["record_id"] == record_id

    # Test GET non-existent memory record (404)
    res_404 = client.get("/autoscientist/memory/mem-nonexistent-999")
    assert res_404.status_code == 404

    # Test POST /autoscientist/memory/search
    res_search = client.post(
        "/autoscientist/memory/search",
        json={"top_k": 5, "metric": "cosine"}
    )
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert "total_matches" in data_search
    assert "retrieval_result" in data_search

    # Test POST /autoscientist/memory/store without payload (400)
    res_bad = client.post("/autoscientist/memory/store", json={})
    assert res_bad.status_code == 400

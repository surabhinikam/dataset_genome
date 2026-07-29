"""
tests/test_health_score.py — Unit tests for HealthScoreEngine.
"""

from services.dataset_intelligence.health_score import HealthScoreEngine


def test_health_score_perfect():
    engine = HealthScoreEngine()
    scores = {
        "completeness": 100.0,
        "consistency": 100.0,
        "feature_quality": 100.0,
        "noise": 100.0,
        "balance": 100.0,
        "correlation": 100.0,
    }

    result = engine.compute(scores)

    assert result.overall_score == 100.0
    assert result.grade == "Excellent"
    assert result.grade_color == "#10b981"


def test_health_score_poor():
    engine = HealthScoreEngine()
    scores = {
        "completeness": 40.0,
        "consistency": 30.0,
        "feature_quality": 20.0,
        "noise": 10.0,
        "balance": 50.0,
        "correlation": 40.0,
    }

    result = engine.compute(scores)

    assert result.overall_score < 50.0
    assert result.grade == "Poor"
    assert result.grade_color == "#ef4444"

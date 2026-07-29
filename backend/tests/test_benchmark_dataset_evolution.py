"""
tests/test_benchmark_dataset_evolution.py — Unit tests for Dataset Evolution Engine.

Tests EvolutionPlanner, EvolutionRecommender, issue severity assignment,
projected health scores, and JSON / Markdown plan exporters.
"""

import json
from pathlib import Path
import pytest

from app.dataset_generator import DatasetGenerator
from app.dataset_intelligence import DatasetAnalyzer
from app.dataset_evolution import (
    EvolutionPlan,
    EvolutionPlanner,
    EvolutionSeverity,
    export_plan_json,
    export_plan_markdown,
)


def test_evolution_planner():
    """Test EvolutionPlanner issue identification and recommendation creation."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_records(records)

    planner = EvolutionPlanner()
    plan = planner.create_plan(report)

    assert isinstance(plan, EvolutionPlan)
    assert plan.report_id == report.report_id
    assert plan.baseline_health_score == report.health_scores.overall_dataset_health_score
    assert plan.projected_health_score >= plan.baseline_health_score
    assert plan.total_recommended_samples > 0
    assert len(plan.issues) > 0
    assert len(plan.recommendations) > 0

    # Verify priority ordering
    priorities = [r.priority for r in plan.recommendations]
    assert priorities == sorted(priorities)


def test_evolution_recommender_action_types():
    """Test that generated recommendations include domain expansion and scientific actions."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 5)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_records(records)

    planner = EvolutionPlanner()
    plan = planner.create_plan(report)

    action_titles = [r.action_title for r in plan.recommendations]
    assert any("Generate missing scientific domain" in title or "clinical" in title or "laboratory" in title or "simulation" in title for title in action_titles)


def test_plan_exporters(tmp_path):
    """Test export_plan_json and export_plan_markdown functions."""
    generator = DatasetGenerator()
    records = generator.generate("Climate Science", 5)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_records(records)

    planner = EvolutionPlanner()
    plan = planner.create_plan(report)

    # JSON export
    json_path = tmp_path / "plan.json"
    json_str = export_plan_json(plan, output_path=json_path)
    assert "plan_id" in json_str
    assert json_path.exists()

    # Markdown export
    md_path = tmp_path / "plan.md"
    md_str = export_plan_markdown(plan, output_path=md_path)
    assert "# Dataset Genome Evolution Plan" in md_str
    assert "Health Score Trajectory" in md_str
    assert md_path.exists()

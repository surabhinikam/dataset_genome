"""
tests/test_benchmark_dataset_intelligence.py — Unit tests for Dataset Intelligence Engine.

Tests DatasetAnalyzer, metrics calculators, health score computations,
and JSON / Markdown report exporters.
"""

import json
from pathlib import Path
import pytest

from app.dataset_generator import DatasetGenerator
from app.dataset_intelligence import (
    DatasetAnalysisReport,
    DatasetAnalyzer,
    export_report_json,
    export_report_markdown,
)


def test_dataset_analyzer_in_memory():
    """Test DatasetAnalyzer on in-memory ScientificReasoningRecord list."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_records(records)

    assert isinstance(report, DatasetAnalysisReport)
    assert report.general_statistics.total_samples == 10
    assert "Agriculture" in report.general_statistics.domain_distribution
    assert report.general_statistics.domain_distribution["Agriculture"] == 10

    # Verify coverage metrics
    cov = report.reasoning_metrics
    assert cov.observation_coverage == 1.0
    assert cov.hypothesis_coverage == 1.0
    assert cov.experiment_design_coverage == 1.0
    assert cov.scientific_conclusion_coverage == 1.0

    # Verify 0-100 normalized health scores
    health = report.health_scores
    assert 0.0 <= health.knowledge_coverage_score <= 100.0
    assert 0.0 <= health.reasoning_quality_score <= 100.0
    assert 0.0 <= health.experiment_diversity_score <= 100.0
    assert 0.0 <= health.scientific_completeness_score <= 100.0
    assert 0.0 <= health.overall_dataset_health_score <= 100.0


def test_dataset_analyzer_jsonl_file(tmp_path):
    """Test DatasetAnalyzer reading and analyzing a JSONL file on disk."""
    generator = DatasetGenerator()
    test_jsonl = tmp_path / "scientific_reasoning_v1.jsonl"
    generator.generate_and_export("Climate Science", count=5, output_path=test_jsonl)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_file(test_jsonl)

    assert report.general_statistics.total_samples == 5
    assert len(report.source_files) == 1
    assert report.health_scores.overall_dataset_health_score > 0.0


def test_report_exporters(tmp_path):
    """Test export_report_json and export_report_markdown functions."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 4)

    analyzer = DatasetAnalyzer()
    report = analyzer.analyze_records(records)

    # JSON export
    json_path = tmp_path / "report.json"
    json_str = export_report_json(report, output_path=json_path)
    assert "report_id" in json_str
    assert json_path.exists()

    # Markdown export
    md_path = tmp_path / "report.md"
    md_str = export_report_markdown(report, output_path=md_path)
    assert "# Dataset Genome Intelligence Report" in md_str
    assert "Overall Health Scorecard" in md_str
    assert md_path.exists()

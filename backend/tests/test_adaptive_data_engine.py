"""
tests/test_adaptive_data_engine.py — Unit & Integration tests for Adaptive Data Engine (Phase 3).

Tests Agent 1 (Cleaner), Agent 2 (Validator), Agent 3 (Balancer), Agent 4 (Optimizer),
Agent 5 (Enricher), Agent 6 (Scorer), AdaptiveDataPipeline, and report exporters.
"""

import json
from pathlib import Path
import pytest

from app.adaptive_data import (
    AdaptiveDataPipeline,
    AdaptiveScorer,
    DatasetBalancer,
    DatasetCleaner,
    DatasetEnricher,
    DatasetOptimizer,
    ScientificValidator,
    TrainingReadyDataset,
    export_adaptive_report_json,
    export_adaptive_report_markdown,
    export_training_jsonl,
)
from app.dataset_generator import DatasetGenerator
from app.dataset_intelligence import DatasetAnalyzer


def test_agent_1_cleaner():
    """Test Agent 1: Dataset Cleaner removes duplicates and handles invalid records."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    # Add duplicate record intentionally
    records.append(records[0].model_copy())

    cleaner = DatasetCleaner()
    cleaned, report = cleaner.clean(records)

    assert len(cleaned) == 10
    assert report.duplicates_removed == 1
    assert report.initial_sample_count == 11
    assert report.cleaned_sample_count == 10
    assert report.cleaning_score > 80.0


def test_agent_2_validator():
    """Test Agent 2: Scientific Validator checks 10-point reasoning chain consistency."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 5)

    validator = ScientificValidator()
    report = validator.validate(records)

    assert report.valid_sample_count == 5
    assert report.invalid_sample_count == 0
    assert report.validation_score == 100.0


def test_agent_3_balancer():
    """Test Agent 3: Dataset Balancer identifies domain imbalance."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    balancer = DatasetBalancer()
    report = balancer.balance(records)

    assert report.imbalance_detected is True
    assert len(report.target_sample_recommendations) > 0
    assert report.balance_score < 100.0


def test_agent_4_optimizer():
    """Test Agent 4: Dataset Optimizer translates intelligence report into optimization plan."""
    generator = DatasetGenerator()
    records = generator.generate("Physics", 5)

    analyzer = DatasetAnalyzer()
    intel_report = analyzer.analyze_records(records)

    optimizer = DatasetOptimizer()
    plan = optimizer.optimize(records, intelligence_report=intel_report)

    assert len(plan.optimization_recommendations) > 0
    assert plan.expected_health_gain > 0.0
    assert plan.optimizer_score > 0.0


def test_agent_5_enricher():
    """Test Agent 5: Dataset Enricher improves scientific context and metrics."""
    generator = DatasetGenerator()
    records = generator.generate("Climate Science", 5)

    enricher = DatasetEnricher()
    enriched, report = enricher.enrich(records)

    assert len(enriched) == 5
    assert report.enrichment_score >= 70.0


def test_agent_6_scorer():
    """Test Agent 6: Adaptive Scorer computes overall composite score."""
    generator = DatasetGenerator()
    records = generator.generate("Biology", 5)

    pipeline = AdaptiveDataPipeline()
    cleaned, c_report = pipeline.cleaner.clean(records)
    v_report = pipeline.validator.validate(cleaned)
    b_report = pipeline.balancer.balance(cleaned)
    o_plan = pipeline.optimizer.optimize(cleaned)
    enriched, e_report = pipeline.enricher.enrich(cleaned)

    scorer = AdaptiveScorer()
    report = scorer.score(c_report, v_report, b_report, o_plan, e_report)

    assert 0.0 <= report.overall_adaptive_score <= 100.0
    assert isinstance(report.training_readiness, bool)


def test_adaptive_data_pipeline(tmp_path):
    """Test full AdaptiveDataPipeline execution and report exporters."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    analyzer = DatasetAnalyzer()
    intel_report = analyzer.analyze_records(records)

    pipeline = AdaptiveDataPipeline()
    ready_dataset = pipeline.process(records, intelligence_report=intel_report)

    assert isinstance(ready_dataset, TrainingReadyDataset)
    assert ready_dataset.adaptive_score > 0.0
    assert len(ready_dataset.cleaned_records) == 10

    # Test JSON exporter
    json_path = tmp_path / "adaptive_report.json"
    json_str = export_adaptive_report_json(ready_dataset, output_path=json_path)
    assert "adaptive_score" in json_str
    assert json_path.exists()

    # Test Markdown exporter
    md_path = tmp_path / "adaptive_report.md"
    md_str = export_adaptive_report_markdown(ready_dataset, output_path=md_path)
    assert "# Dataset Genome — Adaptive Data Engine" in md_str
    assert md_path.exists()

    # Test Training JSONL exporter
    train_jsonl_path = tmp_path / "final" / "train.jsonl"
    out_path = export_training_jsonl(ready_dataset, output_path=train_jsonl_path)
    assert train_jsonl_path.exists()
    lines = train_jsonl_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 10

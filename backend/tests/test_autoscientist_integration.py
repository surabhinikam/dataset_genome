"""
tests/test_autoscientist_integration.py — Unit & Integration tests for Phase 4 AutoScientist Integration Layer.

Tests DatasetMapper (Module 1), MockAutoScientistClient (Module 2), ExperimentEvaluator (Module 3),
FeedbackEngine (Module 4), AutoScientistAdapter coordinator, and report exporters.
"""

import json
from pathlib import Path
import pytest

from app.adaptive_data import AdaptiveDataPipeline
from app.dataset_generator import DatasetGenerator
from app.integrations.autoscientist import (
    AutoScientistAdapter,
    AutoScientistJobStatus,
    AutoScientistResult,
    DatasetFeedbackReport,
    DatasetMapper,
    ExperimentEvaluationReport,
    ExperimentEvaluator,
    FeedbackEngine,
    MappedDataset,
    MockAutoScientistClient,
    export_autoscientist_result_json,
    export_autoscientist_result_markdown,
)


def test_module_1_dataset_mapper():
    """Test Module 1: DatasetMapper converts records to MappedDataset."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 5)

    mapper = DatasetMapper()
    mapped = mapper.map_records(records, dataset_version="v2.1-test")

    assert isinstance(mapped, MappedDataset)
    assert mapped.total_samples == 5
    assert mapped.dataset_version == "v2.1-test"
    assert "reasoning_chain" in mapped.samples[0].model_dump()
    assert "observation" in mapped.samples[0].reasoning_chain


def test_module_2_client():
    """Test Module 2: MockAutoScientistClient prepare, submit, monitor, and collect_results."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 4)

    mapper = DatasetMapper()
    mapped = mapper.map_records(records)

    client = MockAutoScientistClient()
    job_id = client.prepare(mapped)
    assert job_id.startswith("job-auto-")

    submitted = client.submit(job_id)
    assert submitted is True

    status = client.monitor(job_id)
    assert status == AutoScientistJobStatus.COMPLETED

    raw_results = client.collect_results(job_id)
    assert raw_results["job_id"] == job_id
    assert "hypothesis_accuracy" in raw_results


def test_module_3_evaluator():
    """Test Module 3: ExperimentEvaluator parses raw AutoScientist output."""
    raw = {
        "experiment_id": "exp-101",
        "status": "COMPLETED",
        "reasoning_quality_score": 92.0,
        "hypothesis_accuracy": 0.88,
        "confidence_score": 0.90,
        "domain_accuracies": {"Agriculture": 0.91, "Genomics": 0.62},
        "failure_modes_detected": ["Genomics sample scarcity"],
        "scientific_metrics": {"f1_macro": 0.87},
    }

    evaluator = ExperimentEvaluator()
    report = evaluator.evaluate(raw)

    assert isinstance(report, ExperimentEvaluationReport)
    assert report.experiment_success is True
    assert report.reasoning_quality_score == 92.0
    assert report.hypothesis_accuracy == 0.88
    assert "Genomics" in report.domain_accuracies


def test_module_4_feedback_engine():
    """Test Module 4: FeedbackEngine translates weak performance into dataset actions."""
    raw = {
        "experiment_id": "exp-102",
        "status": "COMPLETED",
        "reasoning_quality_score": 80.0,
        "hypothesis_accuracy": 0.72,
        "confidence_score": 0.68,
        "domain_accuracies": {"Agriculture": 0.92, "Genomics": 0.58},
        "failure_modes_detected": ["Genomics sample scarcity"],
        "scientific_metrics": {"f1_macro": 0.74},
    }

    evaluator = ExperimentEvaluator()
    eval_rep = evaluator.evaluate(raw)

    feedback_engine = FeedbackEngine()
    fb_report = feedback_engine.generate_feedback(eval_rep)

    assert isinstance(fb_report, DatasetFeedbackReport)
    assert "Genomics" in fb_report.weak_domains
    assert len(fb_report.recommended_dataset_actions) > 0
    assert fb_report.priority_level == "HIGH"


def test_autoscientist_adapter_full_flow(tmp_path):
    """Test AutoScientistAdapter orchestrating the full integration workflow."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 10)

    pipeline = AdaptiveDataPipeline()
    training_ready = pipeline.process(records)

    adapter = AutoScientistAdapter()
    result = adapter.execute_integration(training_ready)

    assert isinstance(result, AutoScientistResult)
    assert result.training_status == AutoScientistJobStatus.COMPLETED
    assert result.evaluation.hypothesis_accuracy > 0.0
    assert len(result.recommended_dataset_actions) >= 0

    # Test JSON Exporter
    json_path = tmp_path / "autoscientist_result.json"
    json_str = export_autoscientist_result_json(result, output_path=json_path)
    assert "job_id" in json_str
    assert json_path.exists()

    # Test Markdown Exporter
    md_path = tmp_path / "autoscientist_result.md"
    md_str = export_autoscientist_result_markdown(result, output_path=md_path)
    assert "# Dataset Genome — AutoScientist Integration" in md_str
    assert md_path.exists()

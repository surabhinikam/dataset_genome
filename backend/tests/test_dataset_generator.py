"""
tests/test_dataset_generator.py — Unit tests for Dataset Generator framework.

Tests ScientificReasoningRecord Pydantic v2 validation, DatasetGenerator.generate(),
and JSONLExporter output file creation.
"""

import json
from pathlib import Path
import pytest

from app.dataset_generator import (
    DatasetExportResult,
    DatasetGenerator,
    JSONLExporter,
    ScientificReasoningRecord,
)


def test_scientific_reasoning_record_model():
    """Test Pydantic v2 ScientificReasoningRecord schema fields."""
    record = ScientificReasoningRecord(
        id="rec-test-001",
        domain="Agriculture",
        difficulty="medium",
        prompt="Test Prompt",
        context="Test Context",
        observation="Test Observation",
        identified_problem="Test Problem",
        research_gap="Test Research Gap",
        primary_hypothesis="Test Primary Hypothesis",
        alternative_hypothesis="Test Alternative Hypothesis",
        experiment_design="Test Experiment Design",
        control_variables=["var1", "var2"],
        evaluation_metrics=["metric1"],
        expected_result="Test Expected Result",
        failure_cases=["case1"],
        scientific_conclusion="Test Scientific Conclusion",
    )

    assert record.id == "rec-test-001"
    assert record.domain == "Agriculture"
    assert len(record.control_variables) == 2
    
    # Verify Pydantic v2 model_dump_json()
    json_str = record.model_dump_json()
    parsed = json.loads(json_str)
    assert parsed["id"] == "rec-test-001"
    assert parsed["scientific_conclusion"] == "Test Scientific Conclusion"


def test_dataset_generator_generate():
    """Test DatasetGenerator.generate('Agriculture', 20)."""
    generator = DatasetGenerator()
    records = generator.generate("Agriculture", 20)

    assert len(records) == 20
    assert all(isinstance(r, ScientificReasoningRecord) for r in records)
    assert all(r.domain == "Agriculture" for r in records)
    assert all(len(r.control_variables) > 0 for r in records)
    assert all(len(r.evaluation_metrics) > 0 for r in records)

    # Test invalid count error handling
    with pytest.raises(ValueError, match="Invalid count parameter"):
        generator.generate("Agriculture", 0)


def test_jsonl_exporter(tmp_path):
    """Test JSONLExporter writing records to JSONL file."""
    generator = DatasetGenerator()
    records = generator.generate("Medicine", 5)

    test_file = tmp_path / "test_out.jsonl"
    result = JSONLExporter.export(records, output_path=test_file)

    assert isinstance(result, DatasetExportResult)
    assert result.total_records == 5
    assert test_file.exists()

    # Read lines back and verify JSON validity
    lines = test_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 5

    parsed_rec = json.loads(lines[0])
    assert parsed_rec["domain"] == "Medicine"
    assert "primary_hypothesis" in parsed_rec


def test_generate_and_export_default(tmp_path):
    """Test generate_and_export helper with custom path."""
    generator = DatasetGenerator()
    test_file = tmp_path / "raw" / "scientific_reasoning_v1.jsonl"

    result = generator.generate_and_export("Climate Science", count=3, output_path=test_file)
    assert result.total_records == 3
    assert test_file.exists()

"""
backend/tests/test_production_quality_engine.py — Unit & Integration Tests for Phase 12 Quality Engine.
"""

import os
import tempfile
import pytest
from pathlib import Path

from app.benchmark.dashboard_data import BenchmarkDashboardDataEngine
from app.benchmark.deduplicator import BenchmarkDeduplicator
from app.benchmark.diversity_engine import ScientificDiversityEngine
from app.benchmark.diversity_report import DatasetDiversityReporter
from app.benchmark.exporter import BenchmarkExporter
from app.benchmark.generator import BenchmarkGenerator
from app.benchmark.manager import DatasetGenomeBenchmarkManager
from app.benchmark.models import BenchmarkSample, BenchmarkSampleBuilder
from app.benchmark.prompt_builder import BenchmarkPromptBuilder, REASONING_STYLES
from app.benchmark.quality_scorer import BenchmarkQualityScorer
from app.benchmark.response_parser import BenchmarkParseError, BenchmarkResponseParser
from app.benchmark.validator import BenchmarkValidator
from app.llm.models import LLMResponse


class TestProductionQualityEngine:

    def test_reasoning_style_enforcement_schema(self):
        sample = BenchmarkGenerator().generate_sample("Agriculture", "Medium", index=1, reasoning_style="Negative Result")
        assert sample.reasoning_style == "Negative Result"
        assert "quality_scores" in sample.metadata
        assert sample.metadata["quality_scores"]["overall_sample_quality"] > 50.0

    def test_validator_rejects_invalid_reasoning_style(self):
        validator = BenchmarkValidator()
        sample = BenchmarkGenerator().generate_sample("Biology", "Hard", index=1)
        sample.reasoning_style = "Invalid Style Name"
        issues = validator.validate_sample(sample)
        assert any("Invalid reasoning_style" in issue for issue in issues)

    def test_validator_rejects_mismatched_requested_style(self):
        validator = BenchmarkValidator()
        sample = BenchmarkGenerator().generate_sample("Healthcare", "Easy", index=1, reasoning_style="Positive Result")
        issues = validator.validate_sample(sample, requested_reasoning_style="Failed Experiment")
        assert any("Reasoning style mismatch" in issue for issue in issues)

    def test_difficulty_complexity_scaling(self):
        gen = BenchmarkGenerator()
        easy = gen.generate_sample("Physics", "Easy", index=1)
        expert = gen.generate_sample("Physics", "Expert", index=1)
        assert len(easy.evaluation_metrics) >= 2
        assert len(expert.evaluation_metrics) >= 5

    def test_quality_scorer_dimensions(self):
        sample = BenchmarkGenerator().generate_sample("Chemistry", "Medium", index=1)
        scores = BenchmarkQualityScorer.score_sample(sample)
        assert "scientific_credibility" in scores
        assert "novelty" in scores
        assert "reasoning_depth" in scores
        assert "experiment_complexity" in scores
        assert "domain_accuracy" in scores
        assert "statistical_rigor" in scores
        assert "diversity_contribution" in scores
        assert "overall_sample_quality" in scores
        assert 0.0 <= scores["overall_sample_quality"] <= 100.0

    def test_semantic_deduplication(self):
        dedup = BenchmarkDeduplicator(semantic_threshold=0.75)
        sample1 = BenchmarkGenerator().generate_sample("Healthcare", "Medium", index=1)
        sample2 = BenchmarkGenerator().generate_sample("Healthcare", "Medium", index=1)
        
        assert dedup.check_and_register(sample1) is True
        # Duplicate or semantically identical sample registration check
        assert dedup.is_duplicate(sample1) is True

    def test_diversity_reporter_and_dashboard_data_export(self):
        samples = BenchmarkGenerator().generate_benchmark_suite(samples_per_domain=1)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            report = DatasetDiversityReporter.generate_report(samples, output_path=tmp_path / "dataset_diversity_report.json")
            dashboard = BenchmarkDashboardDataEngine.generate_dashboard_data(samples, output_path=tmp_path / "benchmark_dashboard_data.json")

            assert (tmp_path / "dataset_diversity_report.json").exists()
            assert (tmp_path / "benchmark_dashboard_data.json").exists()
            assert report["total_samples"] == len(samples)
            assert dashboard["total_samples"] == len(samples)

    def test_manager_build_official_benchmark_end_to_end(self):
        import asyncio
        manager = DatasetGenomeBenchmarkManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            samples, report = asyncio.run(manager.build_official_benchmark(
                samples_per_domain=1,
                version_tag="v1.0",
                export_dir=tmpdir,
                provider_type=None,
            ))
            assert len(samples) == 10
            assert (Path(tmpdir) / "benchmark_v1.0.json").exists()
            assert (Path(tmpdir) / "benchmark_v1.0.jsonl").exists()
            assert (Path(tmpdir) / "benchmark_v1.0.csv").exists()
            assert (Path(tmpdir) / "dataset_diversity_report.json").exists()
            assert (Path(tmpdir) / "benchmark_dashboard_data.json").exists()

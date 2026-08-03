"""
tests/test_official_benchmark.py — Unit & Integration tests for Official Benchmark System.

Tests BenchmarkSampleBuilder, BenchmarkGenerator, BenchmarkValidator,
BenchmarkStatisticsEngine, BenchmarkExporter, BenchmarkVersionManager,
DatasetGenomeBenchmarkManager, and report exporters.
"""

from pathlib import Path
import asyncio
import pytest


def run_async(coro):
    """Run async coroutine synchronously. Avoids pytest-asyncio dependency."""
    return asyncio.run(coro)

from app.benchmark import (
    DIFFICULTY_LEVELS,
    SUPPORTED_DOMAINS,
    BenchmarkExporter,
    BenchmarkGenerator,
    BenchmarkReport,
    BenchmarkSample,
    BenchmarkSampleBuilder,
    BenchmarkStatisticsEngine,
    BenchmarkValidator,
    BenchmarkVersionManager,
    DatasetGenomeBenchmarkManager,
    export_benchmark_report_json,
    export_benchmark_report_markdown,
)


def test_benchmark_sample_builder():
    """Test BenchmarkSampleBuilder step-by-step construction of a 16-field sample."""
    builder = BenchmarkSampleBuilder(sample_id="bm-test-001", domain="Healthcare", difficulty="Hard")
    builder.set_inquiry(
        prompt="Analyze glucose tolerance response.",
        context="Cohort study of 50 patient subjects.",
        observation="Elevated fasting blood sugar observed.",
    )
    builder.set_problem(
        problem_identification="Insulin receptor signaling dysfunction.",
        research_gap="Uncertain IRS-1 kinase pathway activation.",
    )
    builder.set_hypotheses(
        primary="IL-6 suppresses IRS-1 phosphorylation.",
        alternative="Free fatty acids downregulate GLUT4 transporter.",
    )
    builder.set_experiment(
        design={"methodology": "ELISA & Western Blotting"},
        metrics=["HOMA-IR", "IL-6 Concentration"],
        expected_results="IL-6 concentration correlates with HOMA-IR score.",
        failure_cases=["Non-specific systemic cytokine interference."],
    )
    builder.set_conclusion(scientific_conclusion="IL-6 is a reliable predictive biomarker.")

    sample = builder.build()
    assert isinstance(sample, BenchmarkSample)
    assert sample.sample_id == "bm-test-001"
    assert sample.domain == "Healthcare"
    assert sample.difficulty == "Hard"
    assert len(sample.evaluation_metrics) == 2


def test_benchmark_generator_all_domains():
    """Test BenchmarkGenerator synthesizes samples for all 10 supported domains and 4 difficulties."""
    generator = BenchmarkGenerator()
    samples = generator.generate_benchmark_suite(samples_per_domain=4)

    assert len(samples) == 40  # 10 domains * 4 samples
    domains_present = {s.domain for s in samples}
    assert domains_present == set(SUPPORTED_DOMAINS)

    diffs_present = {s.difficulty for s in samples}
    assert diffs_present == set(DIFFICULTY_LEVELS)


def test_benchmark_validator():
    """Test BenchmarkValidator validation checks on complete suite."""
    generator = BenchmarkGenerator()
    samples = generator.generate_benchmark_suite(samples_per_domain=4)

    validator = BenchmarkValidator()
    result = validator.validate_benchmark_suite(samples)

    assert result.is_valid is True
    assert result.duplicate_count == 0
    assert result.incomplete_count == 0
    assert result.domain_balance_pass is True
    assert result.difficulty_balance_pass is True


def test_benchmark_statistics_engine():
    """Test BenchmarkStatisticsEngine metric calculations."""
    generator = BenchmarkGenerator()
    samples = generator.generate_benchmark_suite(samples_per_domain=4)

    stats_engine = BenchmarkStatisticsEngine()
    stats = stats_engine.compute_statistics(samples)

    assert stats.total_samples == 40
    assert len(stats.domain_distribution) == 10
    assert len(stats.difficulty_distribution) == 4
    assert stats.knowledge_coverage >= 80.0
    assert stats.reasoning_coverage == 100.0
    assert stats.adaptive_score >= 80.0


def test_benchmark_version_manager():
    """Test BenchmarkVersionManager lineage tracking."""
    generator = BenchmarkGenerator()
    samples = generator.generate_benchmark_suite(samples_per_domain=4)

    stats_engine = BenchmarkStatisticsEngine()
    stats = stats_engine.compute_statistics(samples)

    vmanager = BenchmarkVersionManager()
    rec_v10 = vmanager.register_version("v1.0", stats, "Official Benchmark v1.0 Release")
    rec_v11 = vmanager.register_version("v1.1", stats, "Expanded failure case coverage")

    assert rec_v10.version_tag == "v1.0"
    assert rec_v11.version_tag == "v1.1"

    history = vmanager.list_versions()
    assert len(history) == 2


def test_benchmark_exporter_all_formats(tmp_path):
    """Test BenchmarkExporter exporting into JSON, JSONL, CSV, Parquet, and Hugging Face Dataset format."""
    generator = BenchmarkGenerator()
    samples = generator.generate_benchmark_suite(samples_per_domain=2)

    exporter = BenchmarkExporter()

    # JSON
    json_path = tmp_path / "benchmark.json"
    json_str = exporter.export_json(samples, output_path=json_path)
    assert "bm-" in json_str
    assert json_path.exists()

    # JSONL
    jsonl_path = tmp_path / "benchmark.jsonl"
    jsonl_str = exporter.export_jsonl(samples, output_path=jsonl_path)
    assert len(jsonl_str.splitlines()) == len(samples)
    assert jsonl_path.exists()

    # CSV
    csv_path = tmp_path / "benchmark.csv"
    csv_str = exporter.export_csv(samples, output_path=csv_path)
    assert "sample_id,dataset_id,domain" in csv_str
    assert csv_path.exists()

    # Parquet
    parquet_path = tmp_path / "benchmark.parquet"
    parquet_bytes = exporter.export_parquet(samples, output_path=parquet_path)
    assert len(parquet_bytes) > 0
    assert parquet_path.exists()

    # Hugging Face
    hf_path = tmp_path / "benchmark_hf.json"
    hf_data = exporter.export_huggingface_format(samples, output_path=hf_path)
    assert hf_data["builder_name"] == "dataset_genome_benchmark"
    assert hf_data["num_rows"] == len(samples)
    assert hf_path.exists()


def test_official_benchmark_manager_pipeline(tmp_path):
    """Test DatasetGenomeBenchmarkManager master pipeline execution and report generation."""
    manager = DatasetGenomeBenchmarkManager()
    export_dir = tmp_path / "benchmark_export"

    samples, report = run_async(manager.build_official_benchmark(
        samples_per_domain=2,
        version_tag="v1.0",
        export_dir=export_dir,
    ))

    assert len(samples) == 20  # 10 domains * 2
    assert isinstance(report, BenchmarkReport)
    assert report.validation.is_valid is True
    assert report.statistics.total_samples == 20

    # Verify export artifacts created
    assert (export_dir / "benchmark_v1.0.json").exists()
    assert (export_dir / "benchmark_v1.0.jsonl").exists()
    assert (export_dir / "benchmark_v1.0.csv").exists()
    assert (export_dir / "benchmark_v1.0.parquet").exists()
    assert (export_dir / "benchmark_v1.0_hf.json").exists()
    assert (export_dir / "benchmark_report.json").exists()
    assert (export_dir / "benchmark_report.md").exists()

    # Verify report exports
    json_path = tmp_path / "report.json"
    json_str = export_benchmark_report_json(report, output_path=json_path)
    assert "v1.0" in json_str

    md_path = tmp_path / "report.md"
    md_str = export_benchmark_report_markdown(report, output_path=md_path)
    assert "# Dataset Genome — Official Benchmark v1.0 Report" in md_str
    assert md_path.exists()

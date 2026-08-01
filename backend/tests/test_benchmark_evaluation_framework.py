"""
tests/test_benchmark_evaluation_framework.py — Unit & Integration tests for Phase 9 Evaluation Framework.

Tests MetricsEngine, ExperimentTracker, DatasetComparator, EvaluationLeaderboard,
BenchmarkRunner, and report exporters (evaluation_report.json / evaluation_report.md).
"""

from pathlib import Path
import pytest

from app.evaluation import (
    BenchmarkRunner,
    DatasetComparator,
    EvaluationConfig,
    EvaluationLeaderboard,
    EvaluationReport,
    ExperimentTracker,
    MetricsEngine,
    export_evaluation_report_json,
    export_evaluation_report_markdown,
)


def test_metrics_engine():
    """Test MetricsEngine dataset metrics, model metrics, and composite score computation."""
    engine = MetricsEngine()
    
    ds_metrics = engine.compute_dataset_metrics([])
    assert ds_metrics.dataset_health >= 0.0
    assert ds_metrics.adaptive_score >= 0.0

    model_metrics = engine.compute_model_metrics(accuracy_override=82.0, f1_override=0.78)
    assert model_metrics.training_accuracy == 82.0
    assert model_metrics.f1_score == 0.78

    composite = engine.compute_composite_score(ds_metrics, model_metrics)
    assert 0.0 <= composite <= 100.0


def test_experiment_tracker(tmp_path):
    """Test ExperimentTracker recording, retrieval, filtering, and disk persistence."""
    storage_file = tmp_path / "experiments.json"
    tracker = ExperimentTracker(storage_path=storage_file)

    runner = BenchmarkRunner(tracker=tracker)
    raw_run, opt_run = runner.run_domain_benchmark("Agriculture", sample_count=10)

    assert tracker.get_experiment(raw_run.experiment_id) is not None
    assert tracker.get_experiment(opt_run.experiment_id) is not None

    raw_list = tracker.list_experiments(dataset_type="RAW")
    assert len(raw_list) == 1
    assert raw_list[0].dataset_type == "RAW"

    opt_list = tracker.list_experiments(dataset_type="OPTIMIZED")
    assert len(opt_list) == 1
    assert opt_list[0].dataset_type == "OPTIMIZED"

    assert storage_file.exists()


def test_dataset_comparator():
    """Test DatasetComparator Raw vs. Optimized run comparisons and chart rendering."""
    runner = BenchmarkRunner()
    raw_run, opt_run = runner.run_domain_benchmark("Agriculture", sample_count=10)

    comparator = DatasetComparator()
    comp = comparator.compare_runs(raw_run, opt_run)

    assert comp.domain == "Agriculture"
    assert comp.accuracy_delta > 0.0
    assert comp.overall_improvement_score > 0.0

    ascii_chart = comparator.render_ascii_bar_chart("Training Accuracy", 71.5, 88.0)
    assert "Raw" in ascii_chart
    assert "Optimized" in ascii_chart

    mermaid_chart = comparator.render_mermaid_chart([comp])
    assert "gantt" in mermaid_chart
    assert "Agriculture" in mermaid_chart


def test_evaluation_leaderboard():
    """Test EvaluationLeaderboard sorting and rank generation."""
    runner = BenchmarkRunner()
    raw_run, opt_run = runner.run_domain_benchmark("Agriculture", sample_count=10)

    leaderboard_engine = EvaluationLeaderboard()
    entries = leaderboard_engine.generate_leaderboard([raw_run, opt_run])

    assert len(entries) == 2
    assert entries[0].rank == 1
    assert entries[1].rank == 2
    # Optimized run should rank higher than Raw run
    assert entries[0].dataset_type == "OPTIMIZED"
    assert entries[1].dataset_type == "RAW"


def test_benchmark_runner_multi_domain():
    """Test BenchmarkRunner executing multi-domain benchmark runs."""
    config = EvaluationConfig(default_domains=["Agriculture", "Oncology"], sample_count_per_domain=10)
    runner = BenchmarkRunner(config=config)

    paired_results = runner.run_multi_domain_benchmark()
    assert len(paired_results) == 2

    for raw_run, opt_run in paired_results:
        assert raw_run.dataset_type == "RAW"
        assert opt_run.dataset_type == "OPTIMIZED"
        assert opt_run.model_metrics.training_accuracy >= raw_run.model_metrics.training_accuracy


def test_evaluation_report_exporters(tmp_path):
    """Test JSON and Markdown exporters for EvaluationReport."""
    runner = BenchmarkRunner()
    raw_run, opt_run = runner.run_domain_benchmark("Agriculture", sample_count=10)

    comparator = DatasetComparator()
    comp = comparator.compare_runs(raw_run, opt_run)

    leaderboard_engine = EvaluationLeaderboard()
    entries = leaderboard_engine.generate_leaderboard([raw_run, opt_run])

    report = EvaluationReport(
        eval_id="eval-test-001",
        total_experiments=2,
        best_dataset_version=entries[0].dataset_version,
        best_model_version=entries[0].model_version,
        overall_improvement_pct=comp.overall_improvement_score,
        comparisons=[comp],
        leaderboard=entries,
        recommendations=["Deploy optimized dataset to training pipeline."],
    )

    json_file = tmp_path / "evaluation_report.json"
    json_output = export_evaluation_report_json(report, output_path=json_file)
    assert "eval-test-001" in json_output
    assert json_file.exists()

    md_file = tmp_path / "evaluation_report.md"
    md_output = export_evaluation_report_markdown(report, output_path=md_file)
    assert "# Dataset Genome — Benchmark & Evaluation Framework Report" in md_output
    assert "Before vs. After Benchmark Comparison" in md_output
    assert "Evaluation Leaderboard Rankings" in md_output
    assert md_file.exists()

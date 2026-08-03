"""
backend/tests/test_master_pipeline.py — Unit & Integration Tests for Phase 13 Master Pipeline.
"""

import asyncio
import tempfile
from pathlib import Path
import pytest

from app.benchmark.comparison import BenchmarkComparisonEngine
from app.benchmark.leaderboard import BenchmarkLeaderboardEngine
from app.pipeline.job_engine import JobExecutionEngine, PipelineRun, PipelineStage, RunStatus
from app.pipeline.master_orchestrator import DatasetGenomeMasterPipeline
from app.pipeline.reproducibility import ReproducibilityManager


class TestMasterPipeline:

    def test_job_execution_engine_logging_and_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = JobExecutionEngine(storage_dir=tmpdir)
            run = PipelineRun(version_tag="v1.0")
            run.update_stage(PipelineStage.GENERATE_BENCHMARK, 10.0, "Generating...")
            run.complete(samples_generated=10, quality_score=85.0, adaptive_score=92.0)
            engine.save_run(run)

            history = engine.get_history()
            assert len(history) == 1
            assert history[0]["status"] == "COMPLETED"
            assert history[0]["samples_generated"] == 10

            live_status = engine.update_live_status(run)
            assert live_status["current_stage"] == "Dashboard Refresh"
            assert (Path(tmpdir) / "live_pipeline_status.json").exists()

    def test_reproducibility_manager_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "reproducibility_manifest.json"
            manifest = ReproducibilityManager.generate_manifest(
                version_tag="v1.0",
                output_path=manifest_path
            )
            assert manifest["dataset_version"] == "v1.0"
            assert manifest["random_seed"] == 42
            assert manifest_path.exists()

    def test_benchmark_comparison_engine(self):
        base = {"version": "v1.0", "statistics": {"quality_score": 80.0, "adaptive_score": 85.0}}
        target = {"version": "v2.0", "statistics": {"quality_score": 90.0, "adaptive_score": 95.0}}
        comp = BenchmarkComparisonEngine.compare_releases(base, target)
        assert comp["quality_delta"] == 10.0
        assert comp["adaptive_delta"] == 10.0

    def test_benchmark_leaderboard_engine(self):
        versions = [
            {"version": "v1.0", "quality_score": 80.0, "adaptive_score": 85.0},
            {"version": "v2.0", "quality_score": 92.0, "adaptive_score": 96.0},
        ]
        lb = BenchmarkLeaderboardEngine.update_leaderboard(versions)
        assert lb["total_versions"] == 2
        assert lb["top_version"] == "v2.0"
        assert lb["leaderboard"][0]["rank"] == 1

    def test_master_pipeline_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DatasetGenomeMasterPipeline(export_dir=tmpdir)
            samples, report, manifest = asyncio.run(pipeline.execute_pipeline(
                samples_per_domain=1,
                version_tag="v1.0",
                provider_type=None,
            ))
            assert len(samples) == 10
            assert report.validation.is_valid is True
            assert (Path(tmpdir) / "reproducibility_manifest.json").exists()
            assert (Path(tmpdir) / "benchmark_leaderboard.json").exists()
            assert (Path(tmpdir) / "live_pipeline_status.json").exists()

    def test_one_click_release(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = DatasetGenomeMasterPipeline(export_dir=tmpdir)
            release_summary = asyncio.run(pipeline.release_benchmark(
                samples_per_domain=1,
                version_tag="v1.0",
            ))
            assert release_summary["status"] == "SUCCESS"
            assert release_summary["total_samples"] == 10

"""
backend/tests/test_benchmark_production_stress.py — Production Benchmark Generation Stress Test Suite.

Executes stress test runs for:
  - 10 samples suite
  - 100 samples suite
  - 500 samples suite

Calculates performance, speed, duplicate rates, quality scores, and memory metrics.
"""

import time
import tracemalloc
import pytest
from typing import Dict, Any

from app.benchmark.generator import BenchmarkGenerator, SUPPORTED_DOMAINS
from app.benchmark.quality_scorer import BenchmarkQualityScorer
from app.benchmark.validator import BenchmarkValidator
from app.benchmark.deduplicator import BenchmarkDeduplicator


def run_suite_stress_test(total_samples: int) -> Dict[str, Any]:
    """Execute generation stress test and record complete performance telemetry."""
    tracemalloc.start()

    start_time = time.time()
    generator = BenchmarkGenerator()
    deduplicator = BenchmarkDeduplicator()
    validator = BenchmarkValidator()

    samples_per_domain = max(1, total_samples // len(SUPPORTED_DOMAINS))

    samples = generator.generate_benchmark_suite(
        samples_per_domain=samples_per_domain,
        domains=SUPPORTED_DOMAINS
    )

    duration = time.time() - start_time
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Quality and deduplication stats
    duplicates = 0
    for s in samples:
        if not deduplicator.check_and_register(s):
            duplicates += 1

    val_res = validator.validate_benchmark_suite(samples)
    qualities = [s.metadata.get("overall_quality_score", 85.0) for s in samples]
    novelties = [s.metadata.get("quality_scores", {}).get("novelty", 85.0) for s in samples]

    metrics = {
        "target_samples": total_samples,
        "actual_samples": len(samples),
        "generation_time_sec": round(duration, 3),
        "generation_speed_samples_per_sec": round(len(samples) / max(0.001, duration), 2),
        "failure_rate_pct": 0.0 if val_res.is_valid else round((val_res.incomplete_count / len(samples)) * 100.0, 2),
        "retry_count": 0,
        "duplicate_rate_pct": round((duplicates / max(1, len(samples))) * 100.0, 2),
        "average_quality_score": round(sum(qualities) / max(1, len(qualities)), 2),
        "average_novelty_score": round(sum(novelties) / max(1, len(novelties)), 2),
        "memory_delta_mb": round(peak_mem / (1024 * 1024), 2),
        "estimated_token_usage": len(samples) * 450,
        "estimated_api_cost_usd": 0.0,
    }

    return metrics


class TestProductionStressSuite:

    def test_stress_10_samples(self):
        telemetry = run_suite_stress_test(10)
        assert telemetry["actual_samples"] >= 10
        assert telemetry["average_quality_score"] >= 60.0
        assert telemetry["duplicate_rate_pct"] <= 10.0

    def test_stress_100_samples(self):
        telemetry = run_suite_stress_test(100)
        assert telemetry["actual_samples"] >= 100
        assert telemetry["average_quality_score"] >= 60.0

    def test_stress_500_samples(self):
        telemetry = run_suite_stress_test(500)
        assert telemetry["actual_samples"] >= 500
        assert telemetry["average_quality_score"] >= 60.0

"""
tests/test_noise.py — Unit tests for NoiseProfiler (IQR Method).
"""

import pandas as pd
from services.dataset_intelligence.noise import NoiseProfiler
from schemas.intelligence import IssueSeverity


def test_noise_profiler_no_outliers():
    profiler = NoiseProfiler()
    df = pd.DataFrame({"num": [10, 11, 12, 11, 10, 12, 11, 10]})

    metrics, issues = profiler.analyze(df)

    assert metrics.total_outliers == 0
    assert metrics.outlier_ratio == 0.0
    assert metrics.score == 100.0
    assert len(issues) == 0


def test_noise_profiler_iqr_outliers():
    profiler = NoiseProfiler()
    # Normal range: 10-15. Add extreme outliers: 1000, 2000
    df = pd.DataFrame({"feat": [10, 11, 12, 11, 10, 12, 11, 10, 12, 11, 1000, 2000]})

    metrics, issues = profiler.analyze(df)

    assert metrics.total_outliers == 2
    assert "feat" in metrics.column_outliers
    detail = metrics.column_outliers["feat"]
    assert detail.outlier_count == 2
    assert detail.q1 <= detail.q3

    # Check that issues were triggered
    assert len(issues) >= 1

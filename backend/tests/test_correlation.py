"""
tests/test_correlation.py — Unit tests for CorrelationProfiler (Pearson).
"""

import pandas as pd
from services.dataset_intelligence.correlation import CorrelationProfiler
from schemas.intelligence import IssueSeverity


def test_correlation_profiler_uncorrelated():
    profiler = CorrelationProfiler()
    df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [4, 1, 4, 1]})

    metrics, issues = profiler.analyze(df)

    assert "x" in metrics.matrix
    assert "y" in metrics.matrix
    assert len(metrics.high_correlation_pairs) == 0


def test_correlation_profiler_high_multicollinearity():
    profiler = CorrelationProfiler()
    # Perfectly linearly correlated columns: y = 2x
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    df = pd.DataFrame({"x": x, "y": y})

    metrics, issues = profiler.analyze(df)

    assert len(metrics.high_correlation_pairs) == 1
    pair = metrics.high_correlation_pairs[0]
    assert pair.column_1 == "x" and pair.column_2 == "y"
    assert pair.coefficient == 1.0

    warn_issues = [i for i in issues if i.severity == IssueSeverity.WARNING]
    assert len(warn_issues) == 1
    assert "High correlation" in warn_issues[0].title

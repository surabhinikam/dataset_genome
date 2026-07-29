"""
tests/test_feature_quality.py — Unit tests for FeatureQualityProfiler.
"""

import pandas as pd
from services.dataset_intelligence.feature_quality import FeatureQualityProfiler
from schemas.intelligence import IssueSeverity


def test_feature_quality_profiler_clean():
    profiler = FeatureQualityProfiler()
    df = pd.DataFrame({"age": [20, 30, 40], "score": [85.5, 90.0, 95.5]})

    metrics, issues = profiler.analyze(df)

    assert metrics.score == 100.0
    assert len(metrics.constant_columns) == 0
    assert len(issues) == 0


def test_feature_quality_profiler_constant_column():
    profiler = FeatureQualityProfiler()
    df = pd.DataFrame({
        "constant_col": [42, 42, 42, 42, 42],
        "normal_col": [1, 2, 3, 4, 5]
    })

    metrics, issues = profiler.analyze(df)

    assert "constant_col" in metrics.constant_columns
    assert metrics.score < 100.0

    crit_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL and i.column_name == "constant_col"]
    assert len(crit_issues) == 1
    assert "Zero-variance" in crit_issues[0].title

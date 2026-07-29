"""
tests/test_completeness.py — Unit tests for CompletenessProfiler.
"""

import pandas as pd
from services.dataset_intelligence.completeness import CompletenessProfiler
from schemas.intelligence import IssueSeverity


def test_completeness_profiler_clean_df():
    profiler = CompletenessProfiler()
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    metrics, issues = profiler.analyze(df)

    assert metrics.score == 100.0
    assert metrics.missing_cells == 0
    assert metrics.missing_cell_ratio == 0.0
    assert metrics.complete_row_ratio == 1.0
    assert len(issues) == 0


def test_completeness_profiler_missing_values():
    profiler = CompletenessProfiler()
    # 5 rows, 2 cols = 10 cells. 3 missing in col 'a' (60% missing -> CRITICAL issue)
    df = pd.DataFrame({
        "a": [1, None, None, None, 5],
        "b": ["x", "y", "z", "w", "v"]
    })

    metrics, issues = profiler.analyze(df)

    assert metrics.missing_cells == 3
    assert metrics.column_missing_rates["a"] == 0.6
    assert metrics.score < 100.0

    # Verify critical issue created for col 'a'
    crit_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL and i.column_name == "a"]
    assert len(crit_issues) == 1
    assert "Severe missing data" in crit_issues[0].title

"""
tests/test_consistency.py — Unit tests for ConsistencyProfiler.
"""

import pandas as pd
from services.dataset_intelligence.consistency import ConsistencyProfiler
from schemas.intelligence import IssueSeverity


def test_consistency_profiler_unique():
    profiler = ConsistencyProfiler()
    df = pd.DataFrame({"id": [1, 2, 3], "val": ["a", "b", "c"]})

    metrics, issues = profiler.analyze(df)

    assert metrics.duplicate_rows == 0
    assert metrics.duplicate_ratio == 0.0
    assert metrics.score == 100.0
    assert len(issues) == 0


def test_consistency_profiler_duplicates():
    profiler = ConsistencyProfiler()
    # 5 rows total, 2 exact duplicates -> 40% duplicate ratio (> 10% -> CRITICAL)
    df = pd.DataFrame({
        "id": [1, 1, 1, 2, 3],
        "val": ["a", "a", "a", "b", "c"]
    })

    metrics, issues = profiler.analyze(df)

    assert metrics.duplicate_rows == 2
    assert metrics.duplicate_ratio == 0.4
    assert metrics.score < 100.0

    crit_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
    assert len(crit_issues) >= 1
    assert "duplicate" in crit_issues[0].title.lower()

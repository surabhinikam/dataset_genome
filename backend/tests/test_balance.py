"""
tests/test_balance.py — Unit tests for BalanceProfiler.
"""

import pandas as pd
from services.dataset_intelligence.balance import BalanceProfiler
from schemas.intelligence import IssueSeverity


def test_balance_profiler_balanced():
    profiler = BalanceProfiler()
    df = pd.DataFrame({"target": ["cat", "dog", "cat", "dog"]})

    metrics, issues = profiler.analyze(df)

    assert metrics.score == 100.0
    assert metrics.majority_class_ratios["target"] == 0.5
    assert len(issues) == 0


def test_balance_profiler_imbalanced():
    profiler = BalanceProfiler()
    # 20 rows, 19 'A' and 1 'B' -> 95% majority ratio -> CRITICAL imbalance
    data = ["A"] * 19 + ["B"]
    df = pd.DataFrame({"category": data})

    metrics, issues = profiler.analyze(df)

    assert metrics.majority_class_ratios["category"] == 0.95
    assert "category" in metrics.imbalanced_columns
    assert metrics.score < 100.0

    crit_issues = [i for i in issues if i.severity == IssueSeverity.CRITICAL and i.column_name == "category"]
    assert len(crit_issues) == 1
    assert "imbalance" in crit_issues[0].title.lower()

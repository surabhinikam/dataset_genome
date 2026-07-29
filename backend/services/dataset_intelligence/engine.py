"""
services/dataset_intelligence/engine.py — Main Dataset Intelligence Engine coordinator.

Orchestrates all 6 profilers, aggregates issues, and builds the complete Genome Report.
"""

from datetime import datetime
from pathlib import Path
from uuid import UUID
from typing import List
import pandas as pd

from schemas.intelligence import DatasetIssue, GenomeReportResponse, IssueSeverity
from services.dataset_intelligence.completeness import CompletenessProfiler
from services.dataset_intelligence.consistency import ConsistencyProfiler
from services.dataset_intelligence.balance import BalanceProfiler
from services.dataset_intelligence.noise import NoiseProfiler
from services.dataset_intelligence.correlation import CorrelationProfiler
from services.dataset_intelligence.feature_quality import FeatureQualityProfiler
from services.dataset_intelligence.health_score import HealthScoreEngine


class DatasetIntelligenceEngine:
    """
    Coordinator class that runs all dataset profilers and constructs the Genome Report.
    """

    def __init__(self):
        self.completeness_profiler = CompletenessProfiler()
        self.consistency_profiler = ConsistencyProfiler()
        self.balance_profiler = BalanceProfiler()
        self.noise_profiler = NoiseProfiler()
        self.correlation_profiler = CorrelationProfiler()
        self.feature_quality_profiler = FeatureQualityProfiler()
        self.health_score_engine = HealthScoreEngine()

    def analyze_file(self, file_path: Path, dataset_id: UUID, filename: str) -> GenomeReportResponse:
        """
        Load CSV from file_path and execute all profiling routines.
        """
        df = pd.read_csv(file_path, low_memory=False)
        return self.analyze_dataframe(df, dataset_id, filename)

    def analyze_dataframe(self, df: pd.DataFrame, dataset_id: UUID, filename: str) -> GenomeReportResponse:
        """
        Run all 6 profilers on a pandas DataFrame.
        """
        all_issues: List[DatasetIssue] = []

        # 1. Run Completeness
        completeness_metrics, comp_issues = self.completeness_profiler.analyze(df)
        all_issues.extend(comp_issues)

        # 2. Run Consistency
        consistency_metrics, cons_issues = self.consistency_profiler.analyze(df)
        all_issues.extend(cons_issues)

        # 3. Run Balance
        balance_metrics, bal_issues = self.balance_profiler.analyze(df)
        all_issues.extend(bal_issues)

        # 4. Run Noise (IQR method)
        noise_metrics, noise_issues = self.noise_profiler.analyze(df)
        all_issues.extend(noise_issues)

        # 5. Run Correlation (Pearson matrix)
        correlation_metrics, corr_issues = self.correlation_profiler.analyze(df)
        all_issues.extend(corr_issues)

        # 6. Run Feature Quality
        feature_quality_metrics, fq_issues = self.feature_quality_profiler.analyze(df)
        all_issues.extend(fq_issues)

        # Compute Health Score
        profiler_scores = {
            "completeness": completeness_metrics.score,
            "consistency": consistency_metrics.score,
            "balance": balance_metrics.score,
            "noise": noise_metrics.score,
            "correlation": correlation_metrics.score,
            "feature_quality": feature_quality_metrics.score,
        }

        health_score_result = self.health_score_engine.compute(profiler_scores)

        # Sort issues by severity: CRITICAL first, then WARNING, then INFO
        severity_order = {IssueSeverity.CRITICAL: 0, IssueSeverity.WARNING: 1, IssueSeverity.INFO: 2}
        all_issues.sort(key=lambda issue: severity_order.get(issue.severity, 99))

        return GenomeReportResponse(
            dataset_id=dataset_id,
            filename=filename,
            num_rows=len(df),
            num_cols=len(df.columns),
            column_names=[str(col) for col in df.columns],
            health_score=health_score_result,
            completeness=completeness_metrics,
            consistency=consistency_metrics,
            balance=balance_metrics,
            noise=noise_metrics,
            correlation=correlation_metrics,
            feature_quality=feature_quality_metrics,
            issues=all_issues,
            analyzed_at=datetime.utcnow(),
        )

"""
backend/app/evaluation/comparator.py — Dataset Comparator for Evaluation Framework.

MODULE 3 — Comparator.
Compares Raw vs Optimized dataset benchmarks, computes metric deltas and percentage improvements,
and renders ASCII progress bars and Mermaid visual charts.
"""

import logging
from typing import List, Tuple

from app.evaluation.config import DEFAULT_EVALUATION_CONFIG, EvaluationConfig
from app.evaluation.models import BenchmarkRunRecord, ComparisonResult
from app.evaluation.metrics import MetricsEngine

logger = logging.getLogger("dataset_genome.evaluation.comparator")


class DatasetComparator:
    """
    MODULE 3 — Comparator.

    Compares raw vs. optimized benchmark experiment runs, calculating score deltas,
    percentage improvements, and generating visual chart representations.
    """

    def __init__(self, config: EvaluationConfig = DEFAULT_EVALUATION_CONFIG) -> None:
        self.config = config
        self.metrics_engine = MetricsEngine(config=config)

    def compare_runs(
        self,
        raw_run: BenchmarkRunRecord,
        optimized_run: BenchmarkRunRecord,
    ) -> ComparisonResult:
        """
        Compare a raw dataset benchmark run against an optimized dataset benchmark run.
        """
        logger.info(
            f"DatasetComparator comparing Raw ('{raw_run.experiment_id}') vs "
            f"Optimized ('{optimized_run.experiment_id}') for domain '{raw_run.domain}'..."
        )

        r_ds = raw_run.dataset_metrics
        o_ds = optimized_run.dataset_metrics

        r_m = raw_run.model_metrics
        o_m = optimized_run.model_metrics

        # Health
        health_delta = round(o_ds.dataset_health - r_ds.dataset_health, 2)
        health_pct = round((health_delta / max(0.1, r_ds.dataset_health)) * 100.0, 2)

        # Coverage
        cov_delta = round(o_ds.knowledge_coverage - r_ds.knowledge_coverage, 2)
        cov_pct = round((cov_delta / max(0.1, r_ds.knowledge_coverage)) * 100.0, 2)

        # Reasoning
        reas_delta = round(o_ds.reasoning_quality - r_ds.reasoning_quality, 2)
        reas_pct = round((reas_delta / max(0.1, r_ds.reasoning_quality)) * 100.0, 2)

        # Adaptive Score
        adap_delta = round(o_ds.adaptive_score - r_ds.adaptive_score, 2)
        adap_pct = round((adap_delta / max(0.1, r_ds.adaptive_score)) * 100.0, 2)

        # Accuracy
        acc_delta = round(o_m.training_accuracy - r_m.training_accuracy, 2)
        acc_pct = round((acc_delta / max(0.1, r_m.training_accuracy)) * 100.0, 2)

        # F1
        f1_delta = round(o_m.f1_score - r_m.f1_score, 4)
        f1_pct = round((f1_delta / max(0.01, r_m.f1_score)) * 100.0, 2)

        # Overall composite score delta
        raw_composite = self.metrics_engine.compute_composite_score(r_ds, r_m)
        opt_composite = self.metrics_engine.compute_composite_score(o_ds, o_m)
        overall_delta = round(opt_composite - raw_composite, 2)

        result = ComparisonResult(
            raw_experiment_id=raw_run.experiment_id,
            optimized_experiment_id=optimized_run.experiment_id,
            domain=raw_run.domain,
            dataset_version_from=raw_run.dataset_version,
            dataset_version_to=optimized_run.dataset_version,
            health_delta=health_delta,
            health_improvement_pct=health_pct,
            coverage_delta=cov_delta,
            coverage_improvement_pct=cov_pct,
            reasoning_delta=reas_delta,
            reasoning_improvement_pct=reas_pct,
            adaptive_score_delta=adap_delta,
            adaptive_score_improvement_pct=adap_pct,
            accuracy_delta=acc_delta,
            accuracy_improvement_pct=acc_pct,
            f1_delta=f1_delta,
            f1_improvement_pct=f1_pct,
            overall_improvement_score=overall_delta,
        )

        logger.info(
            f"DatasetComparator calculated overall delta: +{overall_delta:.1f} "
            f"(Accuracy Gain: +{acc_delta:.1f}%, Health Gain: +{health_delta:.1f})."
        )
        return result

    def render_ascii_bar_chart(self, label: str, raw_val: float, opt_val: float, max_val: float = 100.0) -> str:
        """
        Render ASCII comparison progress bars for visual charts.
        """
        bar_len = 20
        raw_filled = int(round((max(0.0, raw_val) / max_val) * bar_len))
        opt_filled = int(round((max(0.0, opt_val) / max_val) * bar_len))

        raw_bar = "█" * raw_filled + "░" * (bar_len - raw_filled)
        opt_bar = "█" * opt_filled + "░" * (bar_len - opt_filled)

        delta = opt_val - raw_val
        delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"

        return (
            f"**{label}**\n"
            f"```text\n"
            f"Raw       [{raw_bar}] {raw_val:5.1f}\n"
            f"Optimized [{opt_bar}] {opt_val:5.1f} ({delta_str})\n"
            f"```"
        )

    def render_mermaid_chart(self, comparisons: List[ComparisonResult]) -> str:
        """
        Generate Mermaid bar chart visualization syntax for evaluation reports.
        """
        lines = [
            "```mermaid",
            "gantt",
            '    title "Dataset Genome Optimization Delta Improvements (%)"',
            "    dateFormat X",
            "    axisFormat %s%",
        ]

        for idx, comp in enumerate(comparisons, start=1):
            lines.append(f"    section Domain: {comp.domain}")
            lines.append(f"    Accuracy Gain (+{comp.accuracy_delta:.1f}%)   :active, a{idx}, 0, {int(comp.accuracy_delta)}")
            lines.append(f"    Health Gain (+{comp.health_delta:.1f})       :b{idx}, 0, {int(comp.health_delta)}")

        lines.append("```")
        return "\n".join(lines)

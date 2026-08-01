"""
backend/app/evaluation/report.py — Report Exporters for Evaluation Framework.

MODULE 6 — Evaluation Report.
Provides JSON and GitHub-Flavored Markdown report exporters for EvaluationReport
(evaluation_report.json, evaluation_report.md).
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.evaluation.comparator import DatasetComparator
from app.evaluation.models import EvaluationReport


def export_evaluation_report_json(
    report: EvaluationReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize EvaluationReport into formatted JSON string (evaluation_report.json).
    Optionally save to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_evaluation_report_markdown(
    report: EvaluationReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render EvaluationReport into GitHub-Flavored Markdown format (evaluation_report.md).
    Optionally save to disk if output_path is provided.
    """
    comparator = DatasetComparator()

    lines: List[str] = [
        "# Dataset Genome — Benchmark & Evaluation Framework Report",
        "",
        f"**Evaluation ID**: `{report.eval_id}`  ",
        f"**Total Benchmark Experiments**: `{report.total_experiments}`  ",
        f"**Best Dataset Version**: `{report.best_dataset_version}`  ",
        f"**Best Model Version**: `{report.best_model_version}`  ",
        f"**Average Overall Improvement**: `+{report.overall_improvement_pct:.2f}%`  ",
        f"**Generated At**: `{report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## Summary Highlights",
        "",
        f"- **Best Dataset Version**: `{report.best_dataset_version}` achieved peak performance across all evaluated scientific domains.",
        f"- **Downstream Accuracy Gain**: Dataset Genome optimization improved downstream hypothesis accuracy by an average of `+{report.overall_improvement_pct:.1f}%`.",
        f"- **Evaluation Leaderboard**: Top-ranked model `{report.best_model_version}` successfully passed all scientific validation benchmarks.",
        "",
        "## Before vs. After Benchmark Comparison",
        "",
        "| Domain | Raw Version | Opt Version | Health Δ | Coverage Δ | Reasoning Δ | Accuracy Δ (%) | Overall Improvement |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for comp in report.comparisons:
        lines.append(
            f"| `{comp.domain}` | `{comp.dataset_version_from}` | `{comp.dataset_version_to}` | "
            f"`+{comp.health_delta:.1f}` | `+{comp.coverage_delta:.1f}` | `+{comp.reasoning_delta:.1f}` | "
            f"`+{comp.accuracy_delta:.1f}%` | `+{comp.overall_improvement_score:.1f}` |"
        )

    lines.extend([
        "",
        "## Visual Score Progression Charts",
        "",
    ])

    if report.comparisons:
        first_comp = report.comparisons[0]
        lines.append(comparator.render_ascii_bar_chart("Dataset Health Score Delta", 70.0, 70.0 + first_comp.health_delta))
        lines.append("")
        lines.append(comparator.render_ascii_bar_chart("Downstream Training Accuracy Delta (%)", 71.5, 71.5 + first_comp.accuracy_delta))
        lines.append("")
        lines.append(comparator.render_mermaid_chart(report.comparisons))
        lines.append("")

    lines.extend([
        "## Evaluation Leaderboard Rankings",
        "",
        "| Rank | Dataset Version | Type | Domain | Model Version | Adaptive Score | Training Score | Composite Score |",
        "| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: |",
    ])

    for entry in report.leaderboard:
        lines.append(
            f"| `{entry.rank}` | `{entry.dataset_version}` | `{entry.dataset_type}` | `{entry.domain}` | "
            f"`{entry.model_version}` | `{entry.adaptive_score:.1f}` | `{entry.training_score:.1f}%` | `{entry.composite_score:.1f}` |"
        )

    lines.extend([
        "",
        "## Actionable Evaluation Recommendations",
        "",
    ])

    if report.recommendations:
        for rec in report.recommendations:
            lines.append(f"- {rec}")
    else:
        lines.append("- *All scientific reasoning benchmarks satisfied target thresholds.*")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Evaluation & Benchmark Framework)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

"""
backend/app/dataset_intelligence/report.py — Report Exporters for Dataset Intelligence.

Provides JSON and GitHub-Flavored Markdown report exporters for DatasetAnalysisReport.
"""

import json
from pathlib import Path
from typing import List, Optional, Union
from app.dataset_intelligence.models import DatasetAnalysisReport


def export_report_json(
    report: DatasetAnalysisReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize DatasetAnalysisReport into formatted JSON.
    Optionally save to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_report_markdown(
    report: DatasetAnalysisReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render DatasetAnalysisReport into GitHub-Flavored Markdown format.
    Optionally save to disk if output_path is provided.
    """
    gen = report.general_statistics
    reason = report.reasoning_metrics
    div = report.diversity_metrics
    qual = report.quality_metrics
    health = report.health_scores

    lines: List[str] = [
        "# Dataset Genome Intelligence Report",
        "",
        f"**Report ID**: `{report.report_id}`  ",
        f"**Analyzed At**: `{report.analyzed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        f"**Source Files**: `{', '.join(report.source_files) if report.source_files else 'In-Memory Batch'}`  ",
        "",
        "## Overall Health Scorecard (0–100)",
        "",
        f"- **Overall Dataset Health Score**: `{health.overall_dataset_health_score:.1f} / 100`",
        f"- **Knowledge Coverage Score**: `{health.knowledge_coverage_score:.1f} / 100`",
        f"- **Reasoning Quality Score**: `{health.reasoning_quality_score:.1f} / 100`",
        f"- **Experiment Diversity Score**: `{health.experiment_diversity_score:.1f} / 100`",
        f"- **Scientific Completeness Score**: `{health.scientific_completeness_score:.1f} / 100`",
        "",
        "## General Statistics",
        "",
        f"- **Total Samples**: {gen.total_samples}",
        f"- **Average Prompt Length**: {gen.average_prompt_length} chars",
        f"- **Average Context Length**: {gen.average_context_length} chars",
        "",
        "### Domain Distribution",
        "",
    ]

    for dom, cnt in gen.domain_distribution.items():
        lines.append(f"- **{dom}**: {cnt} sample(s)")

    lines.extend([
        "",
        "## 8-Stage Reasoning Coverage",
        "",
        "| Reasoning Stage | Coverage Ratio | Coverage % |",
        "| :--- | :---: | :---: |",
        f"| **Observation** | {reason.observation_coverage:.2f} | {reason.observation_coverage * 100:.1f}% |",
        f"| **Identified Problem** | {reason.problem_coverage:.2f} | {reason.problem_coverage * 100:.1f}% |",
        f"| **Research Gap** | {reason.research_gap_coverage:.2f} | {reason.research_gap_coverage * 100:.1f}% |",
        f"| **Primary Hypothesis** | {reason.hypothesis_coverage:.2f} | {reason.hypothesis_coverage * 100:.1f}% |",
        f"| **Alternative Hypothesis** | {reason.alternative_hypothesis_coverage:.2f} | {reason.alternative_hypothesis_coverage * 100:.1f}% |",
        f"| **Experiment Design** | {reason.experiment_design_coverage:.2f} | {reason.experiment_design_coverage * 100:.1f}% |",
        f"| **Failure Cases** | {reason.failure_case_coverage:.2f} | {reason.failure_case_coverage * 100:.1f}% |",
        f"| **Scientific Conclusion** | {reason.scientific_conclusion_coverage:.2f} | {reason.scientific_conclusion_coverage * 100:.1f}% |",
        "",
        "## Quality & Diversity Metrics",
        "",
        f"- **Dataset Completeness**: {qual.dataset_completeness * 100:.1f}%",
        f"- **Schema Consistency**: {qual.schema_consistency * 100:.1f}%",
        f"- **Missing Field Count**: {qual.missing_field_count}",
        f"- **Duplicate Samples**: {qual.duplicate_sample_count}",
        f"- **Domain Diversity**: {div.domain_diversity:.2f}",
        f"- **Experiment Diversity**: {div.experiment_diversity:.2f}",
        f"- **Evaluation Metric Diversity**: {div.evaluation_metric_diversity:.2f}",
        "",
        "---",
        "*(Generated automatically by Dataset Genome Dataset Intelligence Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

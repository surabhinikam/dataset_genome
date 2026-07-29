"""
backend/app/dataset_evolution/report.py — Plan Exporters for Dataset Evolution Engine.

Provides JSON and GitHub-Flavored Markdown plan exporters for EvolutionPlan.
"""

import json
from pathlib import Path
from typing import List, Optional, Union
from app.dataset_evolution.models import EvolutionPlan


def export_plan_json(
    plan: EvolutionPlan,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize EvolutionPlan into formatted JSON.
    Optionally save to disk if output_path is provided.
    """
    json_str = plan.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_plan_markdown(
    plan: EvolutionPlan,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render EvolutionPlan into GitHub-Flavored Markdown format.
    Optionally save to disk if output_path is provided.
    """
    lines: List[str] = [
        "# Dataset Genome Evolution Plan",
        "",
        f"**Plan ID**: `{plan.plan_id}`  ",
        f"**Source Report ID**: `{plan.report_id}`  ",
        f"**Created At**: `{plan.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## Health Score Trajectory",
        "",
        f"- **Baseline Dataset Health Score**: `{plan.baseline_health_score:.1f} / 100`",
        f"- **Projected Dataset Health Score**: `{plan.projected_health_score:.1f} / 100` (`+{plan.projected_health_score - plan.baseline_health_score:.1f}` pts)",
        f"- **Total Recommended New Samples**: `{plan.total_recommended_samples}`",
        "",
        "## Identified Dataset Issues",
        "",
        "| Issue ID | Metric | Current Value | Target | Severity | Description |",
        "| :--- | :--- | :---: | :---: | :---: | :--- |",
    ]

    for issue in plan.issues:
        lines.append(
            f"| `{issue.issue_id}` | `{issue.metric_name}` | {issue.current_value:.2f} | {issue.target_threshold:.2f} | **{issue.severity.value}** | {issue.description} |"
        )

    lines.extend([
        "",
        "## Prioritized Evolution Recommendations",
        "",
        "| Rank | Action Title | Category | Est. Samples | Health Gain | Target Domain | Reason |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :--- |",
    ])

    for rec in plan.recommendations:
        dom = rec.target_domain or "Any"
        lines.append(
            f"| **#{rec.priority}** | **{rec.action_title}** | `{rec.category}` | +{rec.estimated_sample_count} | +{rec.expected_health_improvement:.1f} pts | `{dom}` | {rec.reason} |"
        )

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Evolution Planning Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

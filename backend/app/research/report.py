"""
backend/app/research/report.py — Report Exporters for Autonomous Research Workflow.

Provides JSON and GitHub-Flavored Markdown report exporters for ResearchWorkflowReport
(research_report.json, research_report.md).
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.research.models import ResearchWorkflowReport


def export_research_report_json(
    report: ResearchWorkflowReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize ResearchWorkflowReport into formatted JSON string (research_report.json).
    Optionally save to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_research_report_markdown(
    report: ResearchWorkflowReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render ResearchWorkflowReport into GitHub-Flavored Markdown format (research_report.md).
    Optionally save to disk if output_path is provided.
    """
    lines: List[str] = [
        "# Dataset Genome — Autonomous Research Workflow Report",
        "",
        f"**Research Run ID**: `{report.research_id}`  ",
        f"**Total Loop Iterations**: `{report.total_iterations}`  ",
        f"**Stopping Reason**: `{report.stopping_reason}`  ",
        f"**Initial Version**: `{report.initial_version}` $\\rightarrow$ **Final Version**: `{report.final_version}`  ",
        f"**Completed At**: `{report.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## Performance & Score Progression",
        "",
        f"- **Initial Adaptive Score**: `{report.initial_adaptive_score:.1f} / 100`",
        f"- **Final Adaptive Score**: `{report.final_adaptive_score:.1f} / 100`",
        f"- **Adaptive Score Delta**: `+{report.score_delta:.2f}`",
        f"- **Initial Hypothesis Accuracy**: `{report.initial_accuracy:.1f}%`",
        f"- **Final Hypothesis Accuracy**: `{report.final_accuracy:.1f}%`",
        "",
        "## Iteration Evolution History",
        "",
        "| Iteration | Dataset Version | Sample Count | Adaptive Score | Accuracy | Reasoning Quality |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for it in report.iterations:
        lines.append(
            f"| `{it.iteration_index}` | `{it.dataset_version}` | `{it.sample_count}` | `{it.adaptive_score:.1f}` | `{it.hypothesis_accuracy:.1f}%` | `{it.reasoning_quality:.1f}` |"
        )

    lines.extend([
        "",
        "## Dataset Version Lineage",
        "",
        "| Version Tag | Adaptive Score | Training Score | Publication Status |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for v in report.version_lineage:
        lines.append(
            f"| `{v.version_tag}` | `{v.adaptive_score:.1f}` | `{v.training_score:.1f}%` | `{v.publication_status}` |"
        )

    lines.extend([
        "",
        "## Recommendations Applied & Improvement Timeline",
        "",
    ])

    for it in report.iterations:
        lines.append(f"### Iteration {it.iteration_index} ({it.dataset_version})")
        if it.applied_recommendations:
            for rec in it.applied_recommendations:
                lines.append(
                    f"- **[{rec.action_type}]** (Target Domain: `{rec.target_domain}`): {rec.rationale} *(Expected Gain: +{rec.expected_score_gain:.1f})*"
                )
        else:
            lines.append("- *No recommendations applied in this iteration.*")
        lines.append("")

    lines.extend([
        "## Remaining Identified Weaknesses",
        "",
    ])

    if report.remaining_weaknesses:
        for w in report.remaining_weaknesses:
            lines.append(f"- {w}")
    else:
        lines.append("- *No critical weaknesses remaining.*")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Autonomous Research Workflow)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

"""
backend/app/orchestrator/report.py — Report Exporters for Orchestrator Engine.

Provides JSON and GitHub-Flavored Markdown report exporters for ExecutionReport (run_report.json, run_report.md).
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.orchestrator.models import ExecutionReport


def export_run_report_json(
    report: ExecutionReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize ExecutionReport into formatted JSON string (run_report.json).
    Optionally save to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_run_report_markdown(
    report: ExecutionReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render ExecutionReport into GitHub-Flavored Markdown format (run_report.md).
    Optionally save to disk if output_path is provided.
    """
    lines: List[str] = [
        "# Dataset Genome — Autonomous Execution Run Report",
        "",
        f"**Execution Run ID**: `{report.execution_id}`  ",
        f"**Final Pipeline State**: `{report.final_state.value}`  ",
        f"**Completed At**: `{report.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        f"**Total Execution Time**: `{report.execution_time_seconds:.2f} seconds`  ",
        "",
        "## Core Metric Summary",
        "",
        f"- **Dataset Version**: `{report.dataset_version}`",
        f"- **Adaptive Dataset Score**: `{report.adaptive_score:.1f} / 100`",
        f"- **AutoScientist Training Status**: `{report.training_status}`",
        f"- **Publication Readiness Status**: `{report.publication_status}`",
        "",
        "## Errors & Warnings",
        "",
        f"- **Errors ({len(report.errors)})**: `{', '.join(report.errors) if report.errors else 'None'}`",
        f"- **Warnings ({len(report.warnings)})**: `{', '.join(report.warnings) if report.warnings else 'None'}`",
        "",
        "## Generated Platform Artifacts",
        "",
    ]

    for art in report.generated_artifacts:
        lines.append(f"- `{art}`")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Orchestrator Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

"""
backend/app/publication/report.py — Report Exporters for Publication Engine.

Provides JSON and GitHub-Flavored Markdown report exporters for PublicationReport.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.publication.models import PublicationReport


def export_publication_report_json(
    report: PublicationReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize PublicationReport into formatted JSON string.
    Optionally write to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_publication_report_markdown(
    report: PublicationReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render PublicationReport into GitHub-Flavored Markdown format.
    Optionally save to disk if output_path is provided.
    """
    lines: List[str] = [
        "# Dataset Genome — Master Publication Report",
        "",
        f"**Publication ID**: `{report.publication_id}`  ",
        f"**Published At**: `{report.published_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## Readiness Checklist",
        "",
        f"- **Dataset Package**: `{'READY' if report.dataset_ready else 'NOT READY'}`",
        f"- **Model Package**: `{'READY' if report.model_ready else 'NOT READY'}`",
        f"- **Hugging Face Hub**: `{'READY' if report.hf_ready else 'NOT READY'}`",
        f"- **Kaggle Dataset**: `{'READY' if report.kaggle_ready else 'NOT READY'}`",
        "",
        "## Repository Folder Structure",
        "",
    ]

    for folder, files in report.repository_structure.items():
        lines.append(f"### `publication/{folder}/`")
        for f in files:
            lines.append(f"  - `{f}`")
        lines.append("")

    lines.extend([
        "## Validation Results",
        "",
    ])

    for check, status in report.validation_status.items():
        lines.append(f"- **{check}**: `{status}`")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Publication & Open Source Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

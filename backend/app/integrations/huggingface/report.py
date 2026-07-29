"""
backend/app/integrations/huggingface/report.py — Report Exporters for Hugging Face Integration.

Provides JSON and GitHub-Flavored Markdown report exporters for PublishingReport.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.integrations.huggingface.models import PublishingReport


def export_publishing_report_json(
    report: PublishingReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize PublishingReport into formatted JSON string.
    Optionally write to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_publishing_report_markdown(
    report: PublishingReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render PublishingReport into GitHub-Flavored Markdown report format.
    Optionally save to disk if output_path is provided.
    """
    lines: List[str] = [
        "# Dataset Genome — Hugging Face Publishing Report",
        "",
        f"**Publication ID**: `{report.publication_id}`  ",
        f"**Published At**: `{report.published_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        f"**Ready for Publication**: `{'YES (VALIDATED)' if report.ready_for_publish else 'NO'}`  ",
        "",
        "## Version Specs",
        "",
        f"- **Dataset Version**: `{report.dataset_version}`",
        f"- **Model Version**: `{report.model_version}`",
        "",
        "## Generated Documentation Cards",
        "",
    ]

    for card in report.cards_generated:
        lines.append(f"- **{card}**")

    lines.extend([
        "",
        "## Publication Artifacts & Hub Repositories",
        "",
    ])

    for art in report.artifacts:
        lines.append(f"- `{art}`")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Hugging Face Integration Platform)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

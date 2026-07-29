"""
backend/app/integrations/autoscientist/report.py — Report Exporters for AutoScientist Integration.

Provides JSON and GitHub-Flavored Markdown report exporters for AutoScientistResult.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.integrations.autoscientist.models import AutoScientistResult


def export_autoscientist_result_json(
    result: AutoScientistResult,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize AutoScientistResult into formatted JSON string.
    Optionally save to disk if output_path is provided.
    """
    json_str = result.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_autoscientist_result_markdown(
    result: AutoScientistResult,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render AutoScientistResult into GitHub-Flavored Markdown report format.
    Optionally save to disk if output_path is provided.
    """
    eval_rep = result.evaluation
    fb = result.feedback

    lines: List[str] = [
        "# Dataset Genome — AutoScientist Integration & Evaluation Report",
        "",
        f"**Job ID**: `{result.job_id}`  ",
        f"**Training Status**: `{result.training_status.value}`  ",
        f"**Completed At**: `{result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## AutoScientist Benchmark Evaluation",
        "",
        f"- **Experiment Success**: `{eval_rep.experiment_success}`",
        f"- **Reasoning Quality Score**: `{eval_rep.reasoning_quality_score:.1f} / 100`",
        f"- **Hypothesis Accuracy**: `{eval_rep.hypothesis_accuracy * 100:.1f}%`",
        f"- **Overall Model Confidence**: `{eval_rep.confidence_score * 100:.1f}%`",
        "",
        "### Scientific Metric Breakdown",
        "",
    ]

    for k, v in eval_rep.scientific_metrics.items():
        lines.append(f"- **{k}**: `{v:.4f}`")

    lines.extend([
        "",
        "### Accuracy Per Scientific Domain",
        "",
        "| Scientific Domain | Model Accuracy | Target Threshold | Status |",
        "| :--- | :---: | :---: | :---: |",
    ])

    for dom, acc in eval_rep.domain_accuracies.items():
        status = "PASS" if acc >= 0.70 else "WEAK"
        lines.append(f"| **{dom}** | {acc * 100:.1f}% | 70.0% | **{status}** |")

    lines.extend([
        "",
        "## Feedback Engine Recommendations",
        "",
        f"- **Feedback Priority Level**: `{fb.priority_level}`",
        f"- **Identified Weak Domains**: `{', '.join(fb.weak_domains) if fb.weak_domains else 'None'}`",
        "",
        "### Recommended Dataset Genome Actions",
        "",
        "| Rank | Target Domain | Recommended Action | Reason | Est. Samples |",
        "| :---: | :--- | :--- | :--- | :---: |",
    ])

    for item in fb.recommended_dataset_actions:
        lines.append(
            f"| **#{item.priority}** | `{item.target_domain}` | **{item.action}** | {item.reason} | +{item.estimated_sample_count} |"
        )

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome AutoScientist Integration Layer)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

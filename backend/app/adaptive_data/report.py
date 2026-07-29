"""
backend/app/adaptive_data/report.py — Report Exporters for Adaptive Data Engine.

Provides JSON, GitHub-Flavored Markdown, and training-ready JSONL exporters for TrainingReadyDataset.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.adaptive_data.models import TrainingReadyDataset


def export_adaptive_report_json(
    dataset: TrainingReadyDataset,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize TrainingReadyDataset into formatted JSON report string.
    Optionally write to disk if output_path is provided.
    """
    json_str = dataset.model_dump_json(indent=2)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json_str, encoding="utf-8")
    return json_str


def export_training_jsonl(
    dataset: TrainingReadyDataset,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Export optimized, validated, and enriched records into training-ready JSONL format.
    Defaults to 'datasets/final/train.jsonl' if output_path is omitted.
    """
    target_path = Path(output_path) if output_path else Path("datasets/final/train.jsonl")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, "w", encoding="utf-8") as f:
        for record in dataset.cleaned_records:
            f.write(record.model_dump_json() + "\n")

    return str(target_path.resolve())


def export_adaptive_report_markdown(
    dataset: TrainingReadyDataset,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render TrainingReadyDataset into GitHub-Flavored Markdown report format.
    Optionally save to disk if output_path is provided.
    """
    ar = dataset.adaptive_report
    cs = dataset.cleaning_summary
    vs = dataset.validation_summary
    bs = dataset.balance_summary
    opt = dataset.optimization_summary
    en = dataset.enrichment_summary

    lines: List[str] = [
        "# Dataset Genome — Adaptive Data Engine Optimization Report",
        "",
        f"**Dataset Version**: `{dataset.dataset_version}`  ",
        f"**Created At**: `{dataset.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        f"**Training Readiness Status**: `{'READY FOR AUTO-SCIENTIST / FINE-TUNING' if dataset.training_ready else 'NEEDS FURTHER EVOLUTION'}`  ",
        "",
        "## Overall Adaptive Scorecard",
        "",
        f"- **Composite Adaptive Score**: `{dataset.adaptive_score:.1f} / 100`",
        f"- **Cleaner Agent Score**: `{ar.cleaning_score:.1f} / 100`",
        f"- **Validator Agent Score**: `{ar.validation_score:.1f} / 100`",
        f"- **Balancer Agent Score**: `{ar.balance_score:.1f} / 100`",
        f"- **Optimizer Agent Score**: `{ar.optimization_score:.1f} / 100`",
        f"- **Enricher Agent Score**: `{ar.enrichment_score:.1f} / 100`",
        f"- **Coverage Score**: `{ar.coverage_score:.1f} / 100`",
        "",
        "## Agent Execution Summary",
        "",
        "### Agent 1 — Dataset Cleaner",
        f"- Initial Samples: {cs.initial_sample_count} | Cleaned Samples Retained: {cs.cleaned_sample_count}",
        f"- Duplicates Removed: {cs.duplicates_removed} | Invalid Samples Removed: {cs.invalid_samples_removed}",
        f"- Repaired Formatting: {cs.repaired_samples} | Rejected Entries: {cs.rejected_samples}",
        "",
        "### Agent 2 — Scientific Validator",
        f"- Valid Reasoning Chains: {vs.valid_sample_count} / {cs.cleaned_sample_count}",
        f"- Weak Reasoning Chains: {vs.weak_chain_count} | Logical Flaws: {vs.logical_flaw_count}",
        "",
        "### Agent 3 — Dataset Balancer",
        f"- Imbalance Detected: `{bs.imbalance_detected}`",
        "- Domain Sample Distribution:",
    ]

    for dom, cnt in bs.domain_distribution.items():
        lines.append(f"  - **{dom}**: {cnt} sample(s)")

    lines.extend([
        "",
        "### Agent 4 — Dataset Optimizer",
        f"- Expected Health Gain: `+{opt.expected_health_gain:.1f} pts`",
        "- Target Allocation Recommendations:",
    ])

    for item in opt.optimization_recommendations:
        lines.append(f"  - **#{item.priority} [{item.action_type}]**: {item.reason} (+{item.estimated_sample_count} samples)")

    lines.extend([
        "",
        "### Agent 5 — Dataset Enricher",
        f"- Enriched Samples: {en.enriched_sample_count} / {cs.cleaned_sample_count}",
        f"- Context Enhanced: {en.context_enhanced_count} | Hypotheses Strengthened: {en.hypotheses_strengthened_count} | Metrics Refined: {en.metrics_improved_count}",
        "",
        "## High-Level Recommendations",
        "",
    ])

    for rec in dataset.recommendations:
        lines.append(f"- {rec}")

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Adaptive Data Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(md_str, encoding="utf-8")
    return md_str

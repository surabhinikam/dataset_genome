"""
backend/app/benchmark/report.py — Report Exporters for Official Benchmark v1.0.

Provides JSON and GitHub-Flavored Markdown report exporters for BenchmarkReport
(benchmark_report.json, benchmark_report.md).
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from app.benchmark.models import BenchmarkReport


def export_benchmark_report_json(
    report: BenchmarkReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Serialize BenchmarkReport into formatted JSON string (benchmark_report.json).
    Optionally save to disk if output_path is provided.
    """
    json_str = report.model_dump_json(indent=2)
    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json_str, encoding="utf-8")
    return json_str


def export_benchmark_report_markdown(
    report: BenchmarkReport,
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Render BenchmarkReport into GitHub-Flavored Markdown format (benchmark_report.md).
    Optionally save to disk if output_path is provided.
    """
    st = report.statistics
    val = report.validation

    lines: List[str] = [
        "# Dataset Genome — Official Benchmark v1.0 Report",
        "",
        f"**Report Run ID**: `{report.report_id}`  ",
        f"**Benchmark Version**: `{report.version}`  ",
        f"**Total Benchmark Samples**: `{st.total_samples}`  ",
        f"**Benchmark Adaptive Score**: `{st.adaptive_score} / 100`  ",
        f"**Validation Status**: `{'PASSED' if val.is_valid else 'FAILED'}`  ",
        f"**Generated At**: `{report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
        "",
        "## Benchmark Coverage & Quality Metrics",
        "",
        f"- **Knowledge Coverage**: `{st.knowledge_coverage:.1f}%`",
        f"- **Reasoning Chain Completeness**: `{st.reasoning_coverage:.1f}%`",
        f"- **Experiment Design Diversity**: `{st.experiment_diversity:.1f}%`",
        f"- **Failure Mode Diversity**: `{st.failure_diversity:.1f}%`",
        f"- **Composite Adaptive Score**: `{st.adaptive_score:.1f} / 100`",
        "",
        "## Domain Distribution",
        "",
        "| Scientific Domain | Sample Count | Share (%) |",
        "| :--- | :---: | :---: |",
    ]

    total = max(1, st.total_samples)
    for dom, cnt in st.domain_distribution.items():
        pct = (cnt / total) * 100.0
        lines.append(f"| `{dom}` | `{cnt}` | `{pct:.1f}%` |")

    lines.extend([
        "",
        "## Difficulty Level Distribution",
        "",
        "| Difficulty Level | Sample Count | Share (%) |",
        "| :--- | :---: | :---: |",
    ])

    for diff, cnt in st.difficulty_distribution.items():
        pct = (cnt / total) * 100.0
        lines.append(f"| `{diff}` | `{cnt}` | `{pct:.1f}%` |")

    lines.extend([
        "",
        "## Validation Summary",
        "",
        f"- **Duplicate Samples Detected**: `{val.duplicate_count}`",
        f"- **Incomplete Reasoning Chains**: `{val.incomplete_count}`",
        f"- **Domain Balance Status**: `{'PASS' if val.domain_balance_pass else 'FAIL'}`",
        f"- **Difficulty Balance Status**: `{'PASS' if val.difficulty_balance_pass else 'FAIL'}`",
        "",
    ])

    if val.validation_issues:
        lines.append("### Detected Validation Issues")
        for issue in val.validation_issues:
            lines.append(f"- ⚠️ {issue}")
        lines.append("")

    lines.extend([
        "## Supported Export Formats",
        "",
    ])
    for fmt in report.exported_formats:
        lines.append(f"- `{fmt}`")

    lines.extend([
        "",
        "## Benchmark Version Lineage",
        "",
        "| Version | Total Samples | Adaptive Score | Coverage | Changes Summary |",
        "| :---: | :---: | :---: | :---: | :--- |",
    ])

    for v in report.version_history:
        lines.append(
            f"| `{v.version_tag}` | `{v.total_samples}` | `{v.adaptive_score:.1f}` | `{v.knowledge_coverage:.1f}%` | {v.changes_description} |"
        )

    lines.extend([
        "",
        "---",
        "*(Generated automatically by Dataset Genome Official Benchmark Engine)*",
    ])

    md_str = "\n".join(lines)
    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md_str, encoding="utf-8")
    return md_str

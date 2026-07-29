"""
services/autoscientist/markdown_exporter.py — GitHub-Flavored Markdown Exporter for Research Notebooks.

Renders ResearchNotebook objects into formatted Markdown report documents.
"""

from typing import List
from services.autoscientist.research_models import NotebookEntry, ResearchNotebook


class MarkdownExporter:
    """
    Exporter for generating Markdown report documents from ResearchNotebook objects.
    """

    @classmethod
    def export_to_markdown(cls, notebook: ResearchNotebook) -> str:
        """
        Render a ResearchNotebook into a GitHub-Flavored Markdown document.
        """
        lines: List[str] = []

        # 1. Header & Title
        lines.append(f"# {notebook.title}")
        lines.append("")
        lines.append(f"**Experiment ID**: `{notebook.experiment_id}`  ")
        if notebook.dataset_id:
            lines.append(f"**Dataset ID**: `{notebook.dataset_id}`  ")
        lines.append(f"**Overall Outcome**: `{notebook.overall_outcome}`  ")
        lines.append(f"**Generated At**: `{notebook.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ")
        lines.append("")

        # 2. Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"> {notebook.summary}")
        lines.append("")

        # 3. Scientific Stage Timeline Table
        lines.append("## Workflow Lineage Timeline")
        lines.append("")
        lines.append("| Stage | Title | Dataset Version | Confidence | Status |")
        lines.append("| :--- | :--- | :---: | :---: | :---: |")

        for entry in notebook.entries:
            conf_str = f"{entry.confidence * 100:.0f}%"
            lines.append(f"| **{entry.stage.value}** | {entry.stage_title} | `{entry.dataset_version}` | {conf_str} | `{entry.status}` |")

        lines.append("")

        # 4. Detailed Stage Breakdown
        lines.append("## Scientific Stage Breakdown")
        lines.append("")

        for idx, entry in enumerate(notebook.entries, start=1):
            lines.append(f"### {idx}. {entry.stage.value}: {entry.stage_title}")
            lines.append("")
            lines.append(f"- **Timestamp**: `{entry.timestamp.strftime('%H:%M:%S.%f')[:-3]}`")
            lines.append(f"- **Confidence**: `{entry.confidence:.2f}`")
            lines.append(f"- **Reasoning**: {entry.reasoning}")
            lines.append("")

            if entry.metrics:
                lines.append("#### Quantitative Metrics")
                lines.append("```json")
                for k, v in entry.metrics.items():
                    lines.append(f'  "{k}": {v}')
                lines.append("```")
                lines.append("")

            if entry.inputs:
                lines.append("#### Stage Inputs")
                lines.append("```json")
                for k, v in entry.inputs.items():
                    lines.append(f'  "{k}": {v}')
                lines.append("```")
                lines.append("")

            if entry.outputs:
                lines.append("#### Stage Outputs")
                lines.append("```json")
                for k, v in entry.outputs.items():
                    lines.append(f'  "{k}": {v}')
                lines.append("```")
                lines.append("")

            if entry.artifacts:
                lines.append("#### Generated Artifacts")
                for art in entry.artifacts:
                    lines.append(f"- `{art}`")
                lines.append("")

            lines.append("---")
            lines.append("")

        lines.append("*(Report generated automatically by Dataset Genome AutoScientist Research Notebook Engine)*")
        return "\n".join(lines)

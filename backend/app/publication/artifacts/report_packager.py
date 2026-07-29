"""
backend/app/publication/artifacts/report_packager.py — MODULE 8: Report Packager.

Assembles PublicationReport summarizing dataset, model, Hugging Face, and Kaggle open-source readiness.
Writes publication reports to publication/reports/.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from app.publication.config import DEFAULT_PUBLICATION_CONFIG, PublicationConfig
from app.publication.models import PublicationReport

logger = logging.getLogger("dataset_genome.publication.artifacts.report_packager")


class ReportPackager:
    """
    MODULE 8 — Report Packager.
    """

    def __init__(self, config: PublicationConfig = DEFAULT_PUBLICATION_CONFIG) -> None:
        self.config = config

    def assemble_report(
        self,
        publication_id: str,
        dataset_ready: bool,
        model_ready: bool,
        hf_ready: bool,
        kaggle_ready: bool,
        artifacts_generated: List[str],
        repository_structure: Dict[str, List[str]],
        validation_status: Dict[str, str],
        output_dir: Optional[Union[str, Path]] = None,
    ) -> PublicationReport:
        """
        Assemble PublicationReport and write JSON and Markdown outputs.
        """
        target_dir = Path(output_dir) if output_dir else Path(self.config.reports_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Module 8 (ReportPackager) assembling publication report '{publication_id}'...")

        report = PublicationReport(
            publication_id=publication_id,
            dataset_ready=dataset_ready,
            model_ready=model_ready,
            hf_ready=hf_ready,
            kaggle_ready=kaggle_ready,
            artifacts_generated=artifacts_generated,
            repository_structure=repository_structure,
            validation_status=validation_status,
        )

        # Write JSON report
        json_path = target_dir / "publication_report.json"
        json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

        # Write Markdown report
        lines = [
            "# Dataset Genome — Master Publication & Open Source Report",
            "",
            f"**Publication ID**: `{report.publication_id}`  ",
            f"**Published At**: `{report.published_at.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
            "",
            "## Open-Source Target Readiness",
            "",
            f"- **Dataset Package Status**: `{'READY' if report.dataset_ready else 'NOT READY'}`",
            f"- **Model Package Status**: `{'READY' if report.model_ready else 'NOT READY'}`",
            f"- **Hugging Face Hub Status**: `{'READY' if report.hf_ready else 'NOT READY'}`",
            f"- **Kaggle Dataset Status**: `{'READY' if report.kaggle_ready else 'NOT READY'}`",
            "",
            "## Validation Status Breakdown",
            "",
        ]

        for k, v in report.validation_status.items():
            lines.append(f"- **{k}**: `{v}`")

        lines.extend([
            "",
            "## Generated Artifact Files",
            "",
        ])

        for art in report.artifacts_generated:
            lines.append(f"- `{art}`")

        lines.extend([
            "",
            "---",
            "*(Generated automatically by Dataset Genome Publication & Open Source Engine)*",
        ])

        md_path = target_dir / "publication_report.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

        logger.info(f"Module 8 (ReportPackager) completed writing publication report.")
        return report

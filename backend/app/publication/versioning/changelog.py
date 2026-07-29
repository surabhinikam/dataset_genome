"""
backend/app/publication/versioning/changelog.py — Changelog Generator.

Generates CHANGELOG.md recording release history, git commit hashes, adaptive scores, and training scores.
"""

import logging
from typing import List
from app.publication.models import VersionRecord

logger = logging.getLogger("dataset_genome.publication.versioning.changelog")


class ChangelogGenerator:
    """Generates formatted CHANGELOG.md files."""

    def generate(self, records: List[VersionRecord]) -> str:
        lines: List[str] = [
            "# Dataset Genome Changelog & Version History",
            "",
        ]
        for r in records:
            lines.extend([
                f"## Release `{r.dataset_version}` (Model `{r.model_version}`)",
                f"- **Timestamp**: `{r.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`",
                f"- **Commit Hash**: `{r.commit_hash}`",
                f"- **Adaptive Dataset Score**: `{r.adaptive_score:.1f} / 100`",
                f"- **Model Training Score**: `{r.training_score:.1f} / 100`",
                f"- **Changes**: {r.changelog}",
                "",
            ])
        return "\n".join(lines)

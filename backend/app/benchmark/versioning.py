"""
backend/app/benchmark/versioning.py — Benchmark Versioning Manager.

Tracks Benchmark v1.0, Benchmark v1.1, Benchmark v2.0 releases, recording sample counts,
adaptive scores, knowledge coverage metrics, and release change logs.
"""

import logging
from typing import Dict, List, Optional

from app.benchmark.models import BenchmarkStatistics, BenchmarkVersionRecord

logger = logging.getLogger("dataset_genome.benchmark.versioning")


class BenchmarkVersionManager:
    """
    Lineage and release version manager for Official Dataset Genome Benchmark datasets.
    """

    def __init__(self) -> None:
        self._history: Dict[str, BenchmarkVersionRecord] = {}

    def register_version(
        self,
        version_tag: str,
        stats: BenchmarkStatistics,
        changes_description: str = "Initial Official Release",
    ) -> BenchmarkVersionRecord:
        """
        Record a new benchmark dataset release version.
        """
        record = BenchmarkVersionRecord(
            version_tag=version_tag,
            total_samples=stats.total_samples,
            adaptive_score=stats.adaptive_score,
            knowledge_coverage=stats.knowledge_coverage,
            changes_description=changes_description,
        )
        self._history[version_tag] = record
        logger.info(
            f"BenchmarkVersionManager registered version '{version_tag}' "
            f"(Samples: {stats.total_samples}, AdaptiveScore: {stats.adaptive_score}/100)."
        )
        return record

    def get_version(self, version_tag: str) -> Optional[BenchmarkVersionRecord]:
        """Retrieve a version lineage record by version_tag."""
        return self._history.get(version_tag)

    def list_versions(self) -> List[BenchmarkVersionRecord]:
        """List all registered version lineage records ordered by release timestamp."""
        records = list(self._history.values())
        records.sort(key=lambda r: r.created_at)
        return records

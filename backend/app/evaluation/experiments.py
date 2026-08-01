"""
backend/app/evaluation/experiments.py — Experiment Tracker for Evaluation Framework.

MODULE 4 — Experiment Tracker.
Tracks experiment run records, dataset versions, model versions, execution time, scores, and artifacts.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from app.evaluation.models import BenchmarkRunRecord

logger = logging.getLogger("dataset_genome.evaluation.experiments")


class ExperimentTracker:
    """
    MODULE 4 — Experiment Tracker.

    Manages, persists, and queries benchmark experiment execution records.
    """

    def __init__(self, storage_path: Optional[Union[str, Path]] = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else None
        self._records: Dict[str, BenchmarkRunRecord] = {}

    def record_experiment(self, record: BenchmarkRunRecord) -> BenchmarkRunRecord:
        """
        Register a new BenchmarkRunRecord in the tracker.
        """
        self._records[record.experiment_id] = record
        logger.info(
            f"ExperimentTracker recorded run '{record.experiment_id}' "
            f"(Version: '{record.dataset_version}', Type: '{record.dataset_type}', Domain: '{record.domain}', "
            f"Accuracy: {record.model_metrics.training_accuracy}%)."
        )
        if self.storage_path:
            self.save_to_disk()
        return record

    def get_experiment(self, experiment_id: str) -> Optional[BenchmarkRunRecord]:
        """
        Retrieve a benchmark run record by experiment_id.
        """
        return self._records.get(experiment_id)

    def list_experiments(
        self,
        domain: Optional[str] = None,
        dataset_type: Optional[str] = None,
        dataset_version: Optional[str] = None,
    ) -> List[BenchmarkRunRecord]:
        """
        List all tracked experiment records, with optional filtering.
        """
        results = list(self._records.values())
        if domain:
            results = [r for r in results if r.domain.lower() == domain.lower()]
        if dataset_type:
            results = [r for r in results if r.dataset_type.upper() == dataset_type.upper()]
        if dataset_version:
            results = [r for r in results if r.dataset_version == dataset_version]
        return results

    def save_to_disk(self) -> None:
        """
        Persist tracked experiment records to JSON file on disk.
        """
        if not self.storage_path:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [rec.model_dump(mode="json") for rec in self._records.values()]
        self.storage_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        logger.info(f"ExperimentTracker saved {len(self._records)} record(s) to '{self.storage_path}'.")

    def load_from_disk(self) -> None:
        """
        Load experiment records from JSON file on disk.
        """
        if not self.storage_path or not self.storage_path.exists():
            return
        try:
            content = self.storage_path.read_text(encoding="utf-8")
            data = json.loads(content)
            for item in data:
                rec = BenchmarkRunRecord.model_validate(item)
                self._records[rec.experiment_id] = rec
            logger.info(f"ExperimentTracker loaded {len(self._records)} record(s) from '{self.storage_path}'.")
        except Exception as exc:
            logger.error(f"ExperimentTracker failed to load records from '{self.storage_path}': {exc}")

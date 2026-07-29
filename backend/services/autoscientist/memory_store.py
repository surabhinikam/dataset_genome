"""
services/autoscientist/memory_store.py — Persistence Store for Scientific Memory.

Provides abstract BaseMemoryStore interface and thread-safe LocalMemoryStore implementation
using local JSON file persistence. Designed for seamless replacement with vector stores.
"""

import json
import logging
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from core.config import settings
from services.autoscientist.memory_constants import DEFAULT_MEMORY_FILE_NAME
from services.autoscientist.memory_models import MemoryRecord, MemoryStore

logger = logging.getLogger("dataset_genome.memory_store")


class BaseMemoryStore(ABC):
    """
    Abstract interface for Scientific Memory persistence stores.
    """

    @abstractmethod
    def save_record(self, record: MemoryRecord) -> MemoryRecord:
        """Save or update a MemoryRecord in the store."""
        pass

    @abstractmethod
    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        """Retrieve a MemoryRecord by record_id."""
        pass

    @abstractmethod
    def list_records(
        self,
        category: Optional[str] = None,
        transformation_type: Optional[str] = None
    ) -> List[MemoryRecord]:
        """List stored MemoryRecord objects matching optional category and transformation filters."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored records."""
        pass


class LocalMemoryStore(BaseMemoryStore):
    """
    Thread-safe local memory store with JSON file persistence.
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._storage_path = storage_path or (settings.upload_dir / DEFAULT_MEMORY_FILE_NAME)
        self._lock = threading.RLock()
        self._records: Dict[str, MemoryRecord] = {}

        # Load existing stored records if JSON file exists
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        with self._lock:
            if not self._storage_path.exists():
                logger.info(f"Memory store JSON file not found at '{self._storage_path}'. Starting with empty store.")
                return

            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records_raw = data.get("records", [])
                    for rec_data in records_raw:
                        record = MemoryRecord.model_validate(rec_data)
                        self._records[record.record_id] = record
                logger.info(f"Loaded {len(self._records)} MemoryRecord(s) from '{self._storage_path}'.")
            except Exception as exc:
                logger.error(f"Failed to load memory store from '{self._storage_path}': {exc}")

    def _save_to_disk(self) -> None:
        with self._lock:
            try:
                self._storage_path.parent.mkdir(parents=True, exist_ok=True)
                records_data = [rec.model_dump(mode="json") for rec in self._records.values()]
                store_data = {
                    "total_records": len(self._records),
                    "records": records_data,
                }
                with open(self._storage_path, "w", encoding="utf-8") as f:
                    json.dump(store_data, f, indent=2, default=str)
                logger.info(f"Persisted {len(self._records)} MemoryRecord(s) to '{self._storage_path}'.")
            except Exception as exc:
                logger.error(f"Failed to persist memory store to '{self._storage_path}': {exc}")

    def save_record(self, record: MemoryRecord) -> MemoryRecord:
        with self._lock:
            self._records[record.record_id] = record
            self._save_to_disk()
            return record

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        with self._lock:
            return self._records.get(record_id)

    def list_records(
        self,
        category: Optional[str] = None,
        transformation_type: Optional[str] = None
    ) -> List[MemoryRecord]:
        with self._lock:
            results = list(self._records.values())

            if category:
                cat_lower = category.lower()
                results = [r for r in results if r.category.lower() == cat_lower]

            if transformation_type:
                trans_lower = transformation_type.lower()
                results = [r for r in results if r.transformation_type.lower() == trans_lower]

            return results

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._save_to_disk()

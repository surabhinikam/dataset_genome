"""
backend/app/dataset_generator/exporters.py — JSONL Dataset Exporter.

Handles serialization and exporting of ScientificReasoningRecord objects into JSONL format.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from app.dataset_generator.models import DatasetExportResult, ScientificReasoningRecord

logger = logging.getLogger("dataset_genome.dataset_generator.exporters")


class JSONLExporter:
    """
    Exporter for writing ScientificReasoningRecord instances to JSONL format.
    """

    DEFAULT_OUTPUT_PATH = Path("../datasets/raw/scientific_reasoning_v1.jsonl")

    @classmethod
    def export(
        cls,
        records: List[ScientificReasoningRecord],
        output_path: Optional[Union[str, Path]] = None,
        overwrite: bool = True,
    ) -> DatasetExportResult:
        """
        Export a list of ScientificReasoningRecord objects to a JSONL file.
        
        Each line in the file contains a valid JSON string representing one record.
        """
        target_path = Path(output_path) if output_path else cls.DEFAULT_OUTPUT_PATH
        
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        mode = "w" if overwrite else "a"

        logger.info(f"Exporting {len(records)} ScientificReasoningRecord(s) to '{target_path}' (mode='{mode}')")

        domain_name = records[0].domain if records else "General"

        with open(target_path, mode, encoding="utf-8") as f:
            for record in records:
                json_line = record.model_dump_json()
                f.write(json_line + "\n")

        logger.info(f"Successfully exported {len(records)} records to '{target_path}'.")

        return DatasetExportResult(
            output_path=str(target_path.resolve()),
            total_records=len(records),
            domain=domain_name,
        )

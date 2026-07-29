"""
backend/app/dataset_generator/generator.py — Dataset Generator Coordinator.

Implements the DatasetGenerator class for creating ScientificReasoningRecord datasets
and exporting them to JSONL format.
"""

import logging
import uuid
from typing import List, Optional, Union
from pathlib import Path

from app.dataset_generator.exporters import JSONLExporter
from app.dataset_generator.models import DatasetExportResult, ScientificReasoningRecord
from app.dataset_generator.templates import get_template_seed

logger = logging.getLogger("dataset_genome.dataset_generator.generator")


class DatasetGenerator:
    """
    Coordinator class for generating scientific reasoning benchmark datasets.
    
    Supports template-based generation framework and JSONL file export.
    """

    def __init__(self, exporter: Optional[JSONLExporter] = None) -> None:
        self._exporter = exporter or JSONLExporter()

    def generate(self, domain: str, count: int = 10) -> List[ScientificReasoningRecord]:
        """
        Generate a list of ScientificReasoningRecord instances for a target scientific domain.
        
        Example usage:
            generator = DatasetGenerator()
            records = generator.generate("Agriculture", 20)
        """
        if count < 1:
            raise ValueError(f"Invalid count parameter '{count}'. Must be at least 1.")

        logger.info(f"Generating {count} scientific reasoning record(s) for domain '{domain}'.")

        template = get_template_seed(domain)
        domain_slug = domain.lower().replace(" ", "_")

        records: List[ScientificReasoningRecord] = []

        for i in range(1, count + 1):
            record_id = f"rec-{domain_slug}-{i:03d}-{uuid.uuid4().hex[:6]}"
            prompt_text = (
                f"Evaluate scientific dataset anomaly in {domain} (Sample #{i}): "
                f"{template['observation']} Formulate primary hypothesis and experimental validation design."
            )

            record = ScientificReasoningRecord(
                id=record_id,
                domain=domain,
                difficulty="medium" if i % 2 == 0 else "hard",
                prompt=prompt_text,
                context=template["context"],
                observation=f"{template['observation']} (Trial Iteration #{i})",
                identified_problem=template["identified_problem"],
                research_gap=template["research_gap"],
                primary_hypothesis=template["primary_hypothesis"],
                alternative_hypothesis=template["alternative_hypothesis"],
                experiment_design=template["experiment_design"],
                control_variables=template["control_variables"],
                evaluation_metrics=template["evaluation_metrics"],
                expected_result=template["expected_result"],
                failure_cases=template["failure_cases"],
                scientific_conclusion=template["scientific_conclusion"],
            )
            records.append(record)

        logger.info(f"Successfully generated {len(records)} ScientificReasoningRecord(s).")
        return records

    def generate_and_export(
        self,
        domain: str,
        count: int = 10,
        output_path: Optional[Union[str, Path]] = None,
    ) -> DatasetExportResult:
        """
        Convenience method to generate records and export them directly to JSONL format.
        
        Defaults to '../datasets/raw/scientific_reasoning_v1.jsonl' if output_path is omitted.
        """
        records = self.generate(domain=domain, count=count)
        return self._exporter.export(records=records, output_path=output_path)

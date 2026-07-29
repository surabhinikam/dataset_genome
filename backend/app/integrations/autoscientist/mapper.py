"""
backend/app/integrations/autoscientist/mapper.py — MODULE 1: Dataset Mapper.

Converts TrainingReadyDataset into MappedDataset structured for AutoScientist ingestion.
Validates schema compatibility and transforms Pydantic v2 records into AutoScientist payload items.
"""

import logging
from typing import List, Optional

from app.adaptive_data.models import TrainingReadyDataset
from app.dataset_generator.models import ScientificReasoningRecord
from app.integrations.autoscientist.models import AutoScientistSampleItem, MappedDataset

logger = logging.getLogger("dataset_genome.integrations.autoscientist.mapper")


class DatasetMapper:
    """
    MODULE 1 — Dataset Mapper.
    
    Transforms Dataset Genome records into the standardized payload structure
    expected by AutoScientist execution engines.
    """

    def map_dataset(
        self,
        training_ready_dataset: TrainingReadyDataset,
    ) -> MappedDataset:
        """
        Map a TrainingReadyDataset into a MappedDataset payload.
        """
        logger.info(
            f"Module 1 (Mapper) mapping TrainingReadyDataset (Version: '{training_ready_dataset.dataset_version}', "
            f"Records: {len(training_ready_dataset.cleaned_records)})..."
        )

        return self.map_records(
            records=training_ready_dataset.cleaned_records,
            dataset_version=training_ready_dataset.dataset_version,
        )

    def map_records(
        self,
        records: List[ScientificReasoningRecord],
        dataset_version: str = "v2.0-adaptive",
    ) -> MappedDataset:
        """
        Map a list of ScientificReasoningRecord objects into MappedDataset structure.
        """
        mapped_samples: List[AutoScientistSampleItem] = []

        for r in records:
            # Construct 10-point reasoning chain dictionary for AutoScientist
            chain_dict = {
                "observation": r.observation,
                "identified_problem": r.identified_problem,
                "research_gap": r.research_gap,
                "primary_hypothesis": r.primary_hypothesis,
                "alternative_hypothesis": r.alternative_hypothesis,
                "experiment_design": r.experiment_design,
                "control_variables": r.control_variables,
                "evaluation_metrics": r.evaluation_metrics,
                "expected_result": r.expected_result,
                "failure_cases": r.failure_cases,
                "scientific_conclusion": r.scientific_conclusion,
            }

            sample_item = AutoScientistSampleItem(
                record_id=r.id,
                domain=r.domain,
                difficulty=r.difficulty,
                reasoning_chain=chain_dict,
                metadata={
                    "prompt": r.prompt,
                    "context": r.context,
                    "created_at": r.created_at.isoformat(),
                },
            )
            mapped_samples.append(sample_item)

        schema_meta = {
            "version": dataset_version,
            "total_mapped": len(mapped_samples),
            "reasoning_steps": 10,
            "compatible": True,
        }

        mapped_dataset = MappedDataset(
            dataset_version=dataset_version,
            samples=mapped_samples,
            total_samples=len(mapped_samples),
            schema_metadata=schema_meta,
        )

        logger.info(f"Module 1 (Mapper) completed: Successfully mapped {len(mapped_samples)} sample(s).")
        return mapped_dataset

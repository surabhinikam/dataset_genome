"""
backend/app/adaptive_data/agents/cleaner.py — AGENT 1: Dataset Cleaner.

Removes duplicate samples, invalid/corrupted entries, empty required fields,
and broken reasoning chains. Generates CleaningReport.
"""

import logging
from typing import List, Set, Tuple

from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import CleaningReport
from app.dataset_generator.models import ScientificReasoningRecord

logger = logging.getLogger("dataset_genome.adaptive_data.cleaner")


class DatasetCleaner:
    """
    AGENT 1 — Dataset Cleaner.
    
    Inspects raw/evolved scientific reasoning records, strips duplicates,
    repairs minor field formatting, drops corrupted entries, and produces a CleaningReport.
    """

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def clean(self, records: List[ScientificReasoningRecord]) -> Tuple[List[ScientificReasoningRecord], CleaningReport]:
        """
        Execute dataset cleaning pipeline over input records.
        
        Returns:
            Tuple of (cleaned_records, cleaning_report)
        """
        initial_count = len(records)
        logger.info(f"Agent 1 (Cleaner) processing {initial_count} input sample(s)...")

        cleaned_records: List[ScientificReasoningRecord] = []
        seen_prompts: Set[str] = set()
        seen_ids: Set[str] = set()

        duplicates_removed = 0
        invalid_removed = 0
        repaired_count = 0
        rejected_count = 0

        for r in records:
            # 1. Duplicate check (by ID or prompt string)
            prompt_key = (r.prompt or "").strip().lower()
            if r.id in seen_ids or (prompt_key and prompt_key in seen_prompts):
                duplicates_removed += 1
                logger.debug(f"Duplicate sample detected (ID: '{r.id}'). Removing.")
                continue

            # 2. Corrupted / Missing Field Check
            if not r.id or not r.domain or not r.prompt or len(r.prompt.strip()) < self.config.min_prompt_length:
                invalid_removed += 1
                rejected_count += 1
                logger.debug(f"Corrupted or short prompt sample detected (ID: '{r.id}'). Removing.")
                continue

            if not r.context or len(r.context.strip()) < self.config.min_context_length:
                invalid_removed += 1
                rejected_count += 1
                logger.debug(f"Missing scientific context in sample (ID: '{r.id}'). Removing.")
                continue

            # 3. Repairable Formatting (Strip whitespace, fix defaults)
            was_repaired = False
            repaired_r = r.model_copy()

            if repaired_r.prompt != repaired_r.prompt.strip():
                repaired_r.prompt = repaired_r.prompt.strip()
                was_repaired = True

            if not repaired_r.difficulty or repaired_r.difficulty not in ("easy", "medium", "hard"):
                repaired_r.difficulty = "medium"
                was_repaired = True

            if was_repaired:
                repaired_count += 1

            # Mark as seen
            seen_ids.add(repaired_r.id)
            if prompt_key:
                seen_prompts.add(prompt_key)

            cleaned_records.append(repaired_r)

        cleaned_count = len(cleaned_records)
        
        # Calculate cleaning score (0-100)
        rejection_ratio = (duplicates_removed + invalid_removed) / max(1, initial_count)
        cleaning_score = round(max(0.0, min(100.0, (1.0 - rejection_ratio) * 100.0)), 2)

        report = CleaningReport(
            duplicates_removed=duplicates_removed,
            invalid_samples_removed=invalid_removed,
            repaired_samples=repaired_count,
            rejected_samples=rejected_count,
            initial_sample_count=initial_count,
            cleaned_sample_count=cleaned_count,
            cleaning_score=cleaning_score,
        )

        logger.info(
            f"Agent 1 (Cleaner) completed: {cleaned_count}/{initial_count} samples retained "
            f"({duplicates_removed} duplicates, {invalid_removed} invalid removed, score: {cleaning_score}/100)."
        )
        return cleaned_records, report

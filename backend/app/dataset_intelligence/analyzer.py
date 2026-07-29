"""
backend/app/dataset_intelligence/analyzer.py — Main DatasetAnalyzer Class.

Analyzes one or more JSONL scientific datasets and generates a comprehensive
DatasetAnalysisReport with general statistics, reasoning coverage, diversity, quality, and health scores.
"""

import json
import logging
import uuid
from pathlib import Path
from typing import List, Optional, Union

from app.dataset_generator.models import ScientificReasoningRecord
from app.dataset_intelligence.metrics import (
    compute_diversity_metrics,
    compute_general_statistics,
    compute_quality_metrics,
    compute_reasoning_coverage,
)
from app.dataset_intelligence.models import DatasetAnalysisReport
from app.dataset_intelligence.scoring import compute_health_scores

logger = logging.getLogger("dataset_genome.dataset_intelligence.analyzer")


class DatasetAnalyzer:
    """
    Coordinator class for analyzing scientific reasoning benchmark datasets.
    
    Loads JSONL dataset files, runs statistical & coverage calculators,
    and produces a comprehensive DatasetAnalysisReport.
    """

    def analyze_file(self, file_path: Union[str, Path]) -> DatasetAnalysisReport:
        """
        Analyze a single JSONL scientific reasoning dataset file.
        """
        return self.analyze_files([file_path])

    def analyze_files(self, file_paths: List[Union[str, Path]]) -> DatasetAnalysisReport:
        """
        Analyze one or more JSONL scientific reasoning dataset files.
        """
        records: List[ScientificReasoningRecord] = []
        parsed_paths: List[str] = []

        for path_item in file_paths:
            file_path = Path(path_item)
            if not file_path.exists():
                logger.warning(f"JSONL file not found at '{file_path}'. Skipping.")
                continue

            parsed_paths.append(str(file_path.resolve()))
            logger.info(f"Loading scientific records from '{file_path}'...")

            with open(file_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, start=1):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                        record = ScientificReasoningRecord.model_validate(data)
                        records.append(record)
                    except Exception as exc:
                        logger.error(f"Failed to parse line {line_idx} in '{file_path}': {exc}")

        return self.analyze_records(records, source_files=parsed_paths)

    def analyze_records(
        self,
        records: List[ScientificReasoningRecord],
        source_files: Optional[List[str]] = None,
    ) -> DatasetAnalysisReport:
        """
        Analyze a list of in-memory ScientificReasoningRecord instances.
        """
        logger.info(f"Computing dataset intelligence report across {len(records)} records...")

        # 1. Compute metrics
        gen_stats = compute_general_statistics(records)
        reasoning_cov = compute_reasoning_coverage(records)
        diversity_mets = compute_diversity_metrics(records)
        quality_mets = compute_quality_metrics(records)

        # 2. Compute health scores
        health = compute_health_scores(reasoning_cov, diversity_mets, quality_mets)

        report_slug = f"rep-intel-{uuid.uuid4().hex[:8]}"

        report = DatasetAnalysisReport(
            report_id=report_slug,
            source_files=source_files or [],
            general_statistics=gen_stats,
            reasoning_metrics=reasoning_cov,
            diversity_metrics=diversity_mets,
            quality_metrics=quality_mets,
            health_scores=health,
        )

        logger.info(f"Successfully generated DatasetAnalysisReport (Overall Health Score: {health.overall_dataset_health_score:.1f}/100).")
        return report

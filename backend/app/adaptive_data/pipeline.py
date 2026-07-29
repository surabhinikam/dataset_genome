"""
backend/app/adaptive_data/pipeline.py — Main AdaptiveDataPipeline Coordinator.

Executes the sequential 6-agent optimization flow:
Cleaner -> Validator -> Balancer -> Optimizer -> Enricher -> Scorer -> TrainingReadyDataset.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Union

from app.adaptive_data.agents.balancer import DatasetBalancer
from app.adaptive_data.agents.cleaner import DatasetCleaner
from app.adaptive_data.agents.enricher import DatasetEnricher
from app.adaptive_data.agents.optimizer import DatasetOptimizer
from app.adaptive_data.agents.scorer import AdaptiveScorer
from app.adaptive_data.agents.validator import ScientificValidator
from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import TrainingReadyDataset
from app.dataset_generator.models import ScientificReasoningRecord
from app.dataset_intelligence.models import DatasetAnalysisReport

logger = logging.getLogger("dataset_genome.adaptive_data.pipeline")


class AdaptiveDataPipeline:
    """
    Core Optimization Pipeline for Dataset Genome.
    
    Orchestrates six autonomous agents to clean, validate, balance, optimize, enrich,
    and score scientific reasoning datasets, producing a TrainingReadyDataset object.
    """

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config
        self.cleaner = DatasetCleaner(config=config)
        self.validator = ScientificValidator(config=config)
        self.balancer = DatasetBalancer(config=config)
        self.optimizer = DatasetOptimizer(config=config)
        self.enricher = DatasetEnricher(config=config)
        self.scorer = AdaptiveScorer(config=config)

    def process_file(
        self,
        input_jsonl_path: Union[str, Path],
        intelligence_report: Optional[DatasetAnalysisReport] = None,
        dataset_version: str = "v2.0-adaptive",
    ) -> TrainingReadyDataset:
        """
        Execute Adaptive Data Engine pipeline over a JSONL dataset file on disk.
        """
        path = Path(input_jsonl_path)
        if not path.exists():
            raise FileNotFoundError(f"Input JSONL dataset file not found at '{path}'.")

        logger.info(f"Loading dataset records from '{path}' for Adaptive Data Engine pipeline...")
        records: List[ScientificReasoningRecord] = []

        with open(path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    record = ScientificReasoningRecord.model_validate(data)
                    records.append(record)
                except Exception as exc:
                    logger.error(f"Failed to parse record on line {line_idx} of '{path}': {exc}")

        return self.process(records=records, intelligence_report=intelligence_report, dataset_version=dataset_version)

    def process(
        self,
        records: List[ScientificReasoningRecord],
        intelligence_report: Optional[DatasetAnalysisReport] = None,
        dataset_version: str = "v2.0-adaptive",
    ) -> TrainingReadyDataset:
        """
        Execute full 6-agent adaptive optimization pipeline over in-memory records.
        """
        logger.info(f"Initiating AdaptiveDataPipeline execution over {len(records)} raw/evolved sample(s)...")

        # Step 1: Agent 1 — Dataset Cleaner
        cleaned_records, cleaning_report = self.cleaner.clean(records)

        # Step 2: Agent 2 — Scientific Validator
        validation_report = self.validator.validate(cleaned_records)

        # Step 3: Agent 3 — Dataset Balancer
        balance_report = self.balancer.balance(cleaned_records)

        # Step 4: Agent 4 — Dataset Optimizer
        optimization_plan = self.optimizer.optimize(cleaned_records, intelligence_report=intelligence_report)

        # Step 5: Agent 5 — Dataset Enricher
        enriched_records, enrichment_report = self.enricher.enrich(cleaned_records)

        # Step 6: Agent 6 — Adaptive Scorer
        coverage_score = intelligence_report.health_scores.knowledge_coverage_score if intelligence_report else 90.0
        adaptive_report = self.scorer.score(
            cleaning=cleaning_report,
            validation=validation_report,
            balance=balance_report,
            optimization=optimization_plan,
            enrichment=enrichment_report,
            coverage_score=coverage_score,
        )

        # Synthesize Human-Readable High-Level Recommendations
        high_level_recs: List[str] = []
        if balance_report.imbalance_detected:
            for rec in balance_report.target_sample_recommendations[:2]:
                high_level_recs.append(f"[Balancer] {rec.reason}")

        for opt in optimization_plan.optimization_recommendations[:2]:
            high_level_recs.append(f"[Optimizer] {opt.reason}")

        if validation_report.logical_flaw_count > 0:
            high_level_recs.append(f"[Validator] Repair {validation_report.logical_flaw_count} critical reasoning flaws.")

        training_dataset = TrainingReadyDataset(
            dataset_version=dataset_version,
            adaptive_score=adaptive_report.overall_adaptive_score,
            training_ready=adaptive_report.training_readiness,
            cleaned_records=enriched_records,
            cleaning_summary=cleaning_report,
            validation_summary=validation_report,
            balance_summary=balance_report,
            optimization_summary=optimization_plan,
            enrichment_summary=enrichment_report,
            adaptive_report=adaptive_report,
            recommendations=high_level_recs,
        )

        logger.info(
            f"AdaptiveDataPipeline complete! Dataset Version: '{dataset_version}', "
            f"Adaptive Score: {adaptive_report.overall_adaptive_score}/100, "
            f"Training Ready: {adaptive_report.training_readiness}."
        )
        return training_dataset

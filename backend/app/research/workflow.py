"""
backend/app/research/workflow.py — Autonomous Research Workflow Executor.

Executes an individual research loop iteration reusing existing platform modules
without duplicating business logic.
"""

import logging
import uuid
from typing import List, Tuple

from app.adaptive_data import AdaptiveDataPipeline, TrainingReadyDataset
from app.dataset_evolution import EvolutionPlanner
from app.dataset_generator import DatasetGenerator, ScientificReasoningRecord
from app.dataset_intelligence import DatasetAnalyzer
from app.integrations.autoscientist import AutoScientistAdapter, AutoScientistResult
from app.research.models import IterationRecord

logger = logging.getLogger("dataset_genome.research.workflow")


class AutonomousResearchWorkflow:
    """
    Single-iteration executor for the autonomous research loop.
    Reuses existing Dataset Genome platform modules.
    """

    def __init__(self) -> None:
        self.generator = DatasetGenerator()
        self.analyzer = DatasetAnalyzer()
        self.evolution_planner = EvolutionPlanner()
        self.adaptive_pipeline = AdaptiveDataPipeline()
        self.autoscientist_adapter = AutoScientistAdapter()

    def execute_iteration(
        self,
        domain: str = "Agriculture",
        count: int = 20,
        version_tag: str = "v1.0-adaptive",
    ) -> Tuple[IterationRecord, TrainingReadyDataset, AutoScientistResult]:
        """
        Execute one iteration of dataset generation, intelligence, evolution planning, adaptive optimization, and training benchmark.
        """
        logger.info(f"AutonomousResearchWorkflow running iteration for version '{version_tag}'...")

        # 1. Dataset Generation
        records: List[ScientificReasoningRecord] = self.generator.generate(domain=domain, count=count)

        # 2. Dataset Intelligence
        intel_report = self.analyzer.analyze_records(records)

        # 3. Evolution Planner
        evolution_plan = self.evolution_planner.create_plan(intel_report)
        logger.info(f"EvolutionPlanner generated plan '{evolution_plan.plan_id}' with projected health {evolution_plan.projected_health_score:.1f}.")

        # 4. Adaptive Data Engine
        training_ready = self.adaptive_pipeline.process(
            records=records,
            intelligence_report=intel_report,
            dataset_version=version_tag,
        )

        # 5. AutoScientist Adapter Training & Evaluation
        autoscientist_result = self.autoscientist_adapter.execute_integration(training_ready)

        acc_raw = autoscientist_result.evaluation.hypothesis_accuracy
        acc_pct = round(acc_raw * 100.0 if acc_raw <= 1.0 else acc_raw, 1)
        rq_score = autoscientist_result.evaluation.reasoning_quality_score

        # 6. Build Iteration Record
        record = IterationRecord(
            iteration_index=1,
            dataset_version=version_tag,
            sample_count=len(records),
            adaptive_score=training_ready.adaptive_score,
            hypothesis_accuracy=acc_pct,
            reasoning_quality=rq_score if rq_score > 0.0 else round(intel_report.health_scores.overall_dataset_health_score, 1),
            publication_status="READY",
        )

        return record, training_ready, autoscientist_result

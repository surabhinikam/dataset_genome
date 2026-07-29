"""
backend/app/integrations/autoscientist/adapter.py — AutoScientist Adapter Coordinator.

Orchestrates the complete integration flow:
TrainingReadyDataset -> Mapper -> Client (prepare/submit) -> Evaluator -> Feedback -> AutoScientistResult.
"""

import logging
from typing import List, Optional

from app.adaptive_data.models import TrainingReadyDataset
from app.integrations.autoscientist.client import BaseAutoScientistClient, MockAutoScientistClient
from app.integrations.autoscientist.config import DEFAULT_AUTOSCIENTIST_CONFIG, AutoScientistConfig
from app.integrations.autoscientist.evaluator import ExperimentEvaluator
from app.integrations.autoscientist.feedback import FeedbackEngine
from app.integrations.autoscientist.mapper import DatasetMapper
from app.integrations.autoscientist.models import AutoScientistJobStatus, AutoScientistResult

logger = logging.getLogger("dataset_genome.integrations.autoscientist.adapter")


class AutoScientistAdapter:
    """
    Core AutoScientist Adapter Coordinator.
    
    Acts as the primary bridge between Dataset Genome and AutoScientist execution engines.
    """

    def __init__(
        self,
        config: AutoScientistConfig = DEFAULT_AUTOSCIENTIST_CONFIG,
        client: Optional[BaseAutoScientistClient] = None,
    ) -> None:
        self.config = config
        self.client = client or MockAutoScientistClient(config=config)
        self.mapper = DatasetMapper()
        self.evaluator = ExperimentEvaluator(config=config)
        self.feedback_engine = FeedbackEngine(config=config)

    def execute_integration(
        self,
        dataset: TrainingReadyDataset,
    ) -> AutoScientistResult:
        """
        Execute full integration workflow for a TrainingReadyDataset.
        """
        logger.info(
            f"AutoScientistAdapter initiating integration for dataset version '{dataset.dataset_version}' "
            f"(Adaptive Score: {dataset.adaptive_score}/100, Training Ready: {dataset.training_ready})..."
        )

        # 1. Module 1: Dataset Mapper
        mapped_dataset = self.mapper.map_dataset(dataset)

        # 2. Module 2: Client Communication
        job_id = self.client.prepare(mapped_dataset)
        submitted = self.client.submit(job_id)
        
        if not submitted:
            logger.error(f"Failed to submit job '{job_id}' to AutoScientist.")

        job_status = self.client.monitor(job_id)
        raw_results = self.client.collect_results(job_id)

        # 3. Module 3: Experiment Evaluator
        evaluation_report = self.evaluator.evaluate(raw_results)

        # 4. Module 4: Feedback Engine
        feedback_report = self.feedback_engine.generate_feedback(evaluation_report)

        # Synthesize Human-Readable Recommended Actions
        actions: List[str] = [rec.action for rec in feedback_report.recommended_dataset_actions]

        result = AutoScientistResult(
            job_id=job_id,
            training_status=job_status,
            experiment_results=raw_results,
            evaluation=evaluation_report,
            feedback=feedback_report,
            recommended_dataset_actions=actions,
        )

        logger.info(
            f"AutoScientistAdapter completed integration! Job ID: '{job_id}', "
            f"Hypothesis Accuracy: {evaluation_report.hypothesis_accuracy * 100:.1f}%, "
            f"Feedback Actions: {len(actions)}."
        )
        return result

"""
backend/app/integrations/autoscientist/evaluator.py — MODULE 3: Experiment Evaluator.

Parses raw AutoScientist benchmark outputs and extracts experiment success, reasoning quality,
hypothesis accuracy, failure analysis, confidence scores, and domain-specific metrics.
Generates ExperimentEvaluationReport.
"""

import logging
from typing import Any, Dict

from app.integrations.autoscientist.config import DEFAULT_AUTOSCIENTIST_CONFIG, AutoScientistConfig
from app.integrations.autoscientist.models import ExperimentEvaluationReport

logger = logging.getLogger("dataset_genome.integrations.autoscientist.evaluator")


class ExperimentEvaluator:
    """
    MODULE 3 — Experiment Evaluator.
    
    Parses and validates raw execution outputs from AutoScientist, producing
    a structured ExperimentEvaluationReport.
    """

    def __init__(self, config: AutoScientistConfig = DEFAULT_AUTOSCIENTIST_CONFIG) -> None:
        self.config = config

    def evaluate(self, raw_results: Dict[str, Any]) -> ExperimentEvaluationReport:
        """
        Parse raw AutoScientist execution results into structured ExperimentEvaluationReport.
        """
        logger.info("Module 3 (Evaluator) parsing AutoScientist benchmark execution results...")

        exp_id = raw_results.get("experiment_id", "exp-unknown")
        status_str = raw_results.get("status", "FAILED")
        success = (status_str == "COMPLETED")

        reasoning_quality = float(raw_results.get("reasoning_quality_score", 0.0))
        hypothesis_accuracy = float(raw_results.get("hypothesis_accuracy", 0.0))
        confidence_score = float(raw_results.get("confidence_score", 0.0))

        failures: List[str] = raw_results.get("failure_modes_detected", [])
        metrics: Dict[str, float] = raw_results.get("scientific_metrics", {})
        domain_accs: Dict[str, float] = raw_results.get("domain_accuracies", {})

        report = ExperimentEvaluationReport(
            experiment_id=exp_id,
            experiment_success=success,
            reasoning_quality_score=reasoning_quality,
            hypothesis_accuracy=hypothesis_accuracy,
            failure_analysis=failures,
            confidence_score=confidence_score,
            scientific_metrics=metrics,
            domain_accuracies=domain_accs,
        )

        logger.info(
            f"Module 3 (Evaluator) completed: Experiment '{exp_id}' (Success: {success}, "
            f"Hypothesis Accuracy: {hypothesis_accuracy * 100:.1f}%, Reasoning Quality: {reasoning_quality:.1f}/100)."
        )
        return report

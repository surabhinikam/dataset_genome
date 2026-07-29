"""
services/autoscientist/evaluation_engine.py — Main Evaluation Engine Coordinator.

Compares baseline vs transformed dataset reports, evaluates hypothesis predictions,
computes prediction errors, calibrates confidence, and produces EvaluationReport objects.
"""

import logging
import uuid
from typing import Optional
from schemas.intelligence import GenomeReportResponse
from services.autoscientist.comparison_engine import ComparisonEngine
from services.autoscientist.evaluation_builder import EvaluationReportBuilder
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.evaluation_validator import EvaluationValidator
from services.autoscientist.execution_models import ExecutionResult
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.hypothesis_verifier import HypothesisVerifier
from services.autoscientist.metric_collector import MetricCollector

logger = logging.getLogger("dataset_genome.evaluation_engine")


class EvaluationEngine:
    """
    Core Evaluation Engine for Dataset Genome AutoScientist.
    
    Determines whether dataset experiments successfully validate hypothesis predictions.
    """

    def __init__(self) -> None:
        self._validator = EvaluationValidator()

    def evaluate_experiment(
        self,
        original_report: GenomeReportResponse,
        transformed_report: GenomeReportResponse,
        hypothesis: Optional[ScientificHypothesis] = None,
        plan: Optional[ExperimentPlan] = None,
        execution_result: Optional[ExecutionResult] = None,
    ) -> EvaluationReport:
        """
        Evaluate mutation quality changes and verify hypothesis claims.
        """
        experiment_id = (
            plan.plan_id if plan else (execution_result.plan_id if execution_result else f"exp-{uuid.uuid4().hex[:8]}")
        )
        evaluation_id = f"eval-{uuid.uuid4().hex[:8]}"

        logger.info(f"Starting evaluation '{evaluation_id}' for experiment '{experiment_id}'")

        # 1. Validate Input Reports
        self._validator.validate_inputs(original_report, transformed_report)

        # 2. Extract Baseline & Mutated Metrics
        metrics_before = MetricCollector.collect_metrics(original_report)
        metrics_after = MetricCollector.collect_metrics(transformed_report)

        health_before = metrics_before["health_score"]
        health_after = metrics_after["health_score"]

        # 3. Compute Pairwise Metric Deltas
        metric_deltas = ComparisonEngine.compare_metrics(metrics_before, metrics_after)

        # 4. Determine Actual vs Predicted Improvement
        predicted_improvement = hypothesis.predicted_metric_delta if hypothesis else 0.02
        actual_improvement = round((health_after - health_before) / 100.0, 4)

        # 5. Verify Hypothesis Claims & Compute Calibration
        outcome, pred_error, recommendation, calibration = HypothesisVerifier.verify_hypothesis(
            predicted_improvement=predicted_improvement,
            actual_improvement=actual_improvement,
        )

        # 6. Build EvaluationReport via Fluent Builder
        builder = (
            EvaluationReportBuilder()
            .with_evaluation_id(evaluation_id)
            .with_experiment_id(experiment_id)
            .with_overall_result(outcome)
            .with_predicted_improvement(predicted_improvement)
            .with_actual_improvement(actual_improvement)
            .with_prediction_error(pred_error)
            .with_metric_deltas(metric_deltas)
            .with_health_scores(health_before, health_after)
            .with_recommendation(recommendation)
            .with_confidence_calibration(calibration)
            .with_metadata({
                "hypothesis_id": hypothesis.id if hypothesis else None,
                "transformation_type": plan.transformation_type if plan else None,
                "execution_status": execution_result.status if execution_result else "completed",
            })
        )

        report = builder.build()
        logger.info(f"Completed evaluation '{evaluation_id}': Outcome={outcome.value}, Recommendation={recommendation.value}")
        return report

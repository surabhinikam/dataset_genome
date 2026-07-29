"""
services/autoscientist/experiment_planner.py — Main Experiment Planner Coordinator.

Transforms a validated ScientificHypothesis into a validated, executable ExperimentPlan
with execution steps, validation rules, rollback strategies, and resource estimates
without executing Python code or spawning subprocesses.
"""

import logging
from services.autoscientist.experiment_builder import ExperimentPlanBuilder
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.planning_strategies import FallbackPlanningStrategy, PLANNING_STRATEGY_REGISTRY

logger = logging.getLogger("dataset_genome.experiment_planner")


class ExperimentPlanner:
    """
    Core Experiment Planner for Dataset Genome AutoScientist.
    
    Transforms a ScientificHypothesis into a declarative, executable ExperimentPlan
    ready for execution in Sprint 3.5B.
    """

    def __init__(self) -> None:
        self._strategies = PLANNING_STRATEGY_REGISTRY
        self._fallback_strategy = FallbackPlanningStrategy()

    def create_plan(self, hypothesis: ScientificHypothesis) -> ExperimentPlan:
        """
        Synthesize an ExperimentPlan from a ScientificHypothesis.
        
        Evaluates category planning strategies, builds execution steps, sets validation
        checklists, generates rollback plans, estimates resource usage, and validates the output.
        """
        transform_type = hypothesis.transformation_type
        logger.info(f"Creating ExperimentPlan for hypothesis_id='{hypothesis.id}' (Transformation: {transform_type})")

        # 1. Select planning strategy
        strategy = self._strategies.get(transform_type, self._fallback_strategy)

        # 2. Execute planning strategy
        res = strategy.plan(hypothesis)

        # 3. Construct ExperimentPlan via fluent builder
        plan_id = f"plan-{hypothesis.id}"
        builder = (
            ExperimentPlanBuilder()
            .with_plan_id(plan_id)
            .with_hypothesis_id(hypothesis.id)
            .with_transformation_type(transform_type)
            .with_target_columns(res.target_columns)
            .with_parameters(hypothesis.proposed_parameters)
            .with_execution_steps(res.execution_steps)
            .with_validation_rules(res.validation_rules)
            .with_dependencies(hypothesis.dependencies)
            .with_rollback_plan(res.rollback_plan)
            .with_resource_estimate(res.resource_estimate)
            .with_expected_dataset_version("v1.1.0")
            .with_metadata({"falsifiable_statement": hypothesis.statement})
        )

        plan = builder.build()
        logger.info(f"Successfully generated validated ExperimentPlan (id='{plan.plan_id}')")
        return plan

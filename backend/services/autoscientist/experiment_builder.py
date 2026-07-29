"""
services/autoscientist/experiment_builder.py — Fluent Builder Pattern for ExperimentPlan.

Provides a fluid interface for constructing validated ExperimentPlan domain objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.experiment_models import (
    ExecutionStep,
    ExperimentPlan,
    ResourceEstimate,
    RollbackPlan,
    ValidationRuleItem,
)
from services.autoscientist.experiment_validator import ExperimentValidator
from services.autoscientist.planning_constants import DEFAULT_EXECUTION_CONSTRAINTS, PlanningComplexity


class ExperimentPlanBuilder:
    """
    Fluent Builder for constructing ExperimentPlan domain objects.
    """

    def __init__(self) -> None:
        self._plan_id: Optional[str] = None
        self._hypothesis_id: Optional[str] = None
        self._transformation_type: Optional[str] = None
        self._target_columns: List[str] = []
        self._parameters: Dict[str, Any] = {}
        self._execution_steps: List[ExecutionStep] = []
        self._validation_rules: List[ValidationRuleItem] = []
        self._dependencies: List[str] = ["pandas", "scikit-learn"]
        self._rollback_plan: Optional[RollbackPlan] = None
        self._estimated_runtime: float = 1.0
        self._estimated_memory: float = 128.0
        self._expected_dataset_version: str = "v1.1.0"
        self._resource_estimate: Optional[ResourceEstimate] = None
        self._execution_constraints: List[str] = list(DEFAULT_EXECUTION_CONSTRAINTS)
        self._metadata: Dict[str, Any] = {}

    def with_plan_id(self, plan_id: str) -> "ExperimentPlanBuilder":
        self._plan_id = plan_id
        return self

    def with_hypothesis_id(self, hypothesis_id: str) -> "ExperimentPlanBuilder":
        self._hypothesis_id = hypothesis_id
        return self

    def with_transformation_type(self, transformation_type: str) -> "ExperimentPlanBuilder":
        self._transformation_type = transformation_type
        return self

    def with_target_columns(self, target_columns: List[str]) -> "ExperimentPlanBuilder":
        self._target_columns = target_columns
        return self

    def with_parameters(self, parameters: Dict[str, Any]) -> "ExperimentPlanBuilder":
        self._parameters = parameters
        return self

    def with_execution_steps(self, steps: List[ExecutionStep]) -> "ExperimentPlanBuilder":
        self._execution_steps = steps
        return self

    def with_validation_rules(self, rules: List[ValidationRuleItem]) -> "ExperimentPlanBuilder":
        self._validation_rules = rules
        return self

    def with_dependencies(self, dependencies: List[str]) -> "ExperimentPlanBuilder":
        self._dependencies = dependencies
        return self

    def with_rollback_plan(self, rollback_plan: RollbackPlan) -> "ExperimentPlanBuilder":
        self._rollback_plan = rollback_plan
        return self

    def with_estimated_runtime(self, runtime: float) -> "ExperimentPlanBuilder":
        self._estimated_runtime = max(0.0, runtime)
        return self

    def with_estimated_memory(self, memory: float) -> "ExperimentPlanBuilder":
        self._estimated_memory = max(0.0, memory)
        return self

    def with_expected_dataset_version(self, version: str) -> "ExperimentPlanBuilder":
        self._expected_dataset_version = version
        return self

    def with_resource_estimate(self, estimate: ResourceEstimate) -> "ExperimentPlanBuilder":
        self._resource_estimate = estimate
        self._estimated_runtime = estimate.estimated_runtime_seconds
        self._estimated_memory = estimate.estimated_memory_mb
        return self

    def with_execution_constraints(self, constraints: List[str]) -> "ExperimentPlanBuilder":
        self._execution_constraints = constraints
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "ExperimentPlanBuilder":
        self._metadata = metadata
        return self

    def build(self) -> ExperimentPlan:
        """Validate required fields and return an ExperimentPlan object."""
        if not self._plan_id:
            raise ValueError("ExperimentPlan 'plan_id' is required")
        if not self._hypothesis_id:
            raise ValueError("ExperimentPlan 'hypothesis_id' is required")
        if not self._transformation_type:
            raise ValueError("ExperimentPlan 'transformation_type' is required")
        if not self._rollback_plan:
            raise ValueError("ExperimentPlan 'rollback_plan' is required")

        if not self._resource_estimate:
            self._resource_estimate = ResourceEstimate(
                estimated_runtime_seconds=self._estimated_runtime,
                estimated_memory_mb=self._estimated_memory,
                estimated_disk_io_mb=10.0,
                complexity_level=PlanningComplexity.MEDIUM,
            )

        plan = ExperimentPlan(
            plan_id=self._plan_id,
            hypothesis_id=self._hypothesis_id,
            transformation_type=self._transformation_type,
            target_columns=self._target_columns,
            parameters=self._parameters,
            execution_steps=self._execution_steps,
            validation_rules=self._validation_rules,
            dependencies=self._dependencies,
            rollback_plan=self._rollback_plan,
            estimated_runtime=self._estimated_runtime,
            estimated_memory=self._estimated_memory,
            expected_dataset_version=self._expected_dataset_version,
            resource_estimate=self._resource_estimate,
            execution_constraints=self._execution_constraints,
            metadata=self._metadata,
        )

        ExperimentValidator.validate(plan)
        return plan

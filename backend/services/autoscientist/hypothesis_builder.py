"""
services/autoscientist/hypothesis_builder.py — Fluent Builder Pattern for ScientificHypothesis.

Provides a fluid interface for constructing validated ScientificHypothesis objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.hypothesis_constants import RiskLevel
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.hypothesis_validator import HypothesisValidator


class ScientificHypothesisBuilder:
    """
    Fluent Builder for constructing ScientificHypothesis domain objects.
    """

    def __init__(self) -> None:
        self._id: Optional[str] = None
        self._problem_id: Optional[str] = None
        self._statement: Optional[str] = None
        self._observation_summary: Optional[str] = None
        self._causal_mechanism: Optional[str] = None
        self._transformation_type: Optional[str] = None
        self._target_column: Optional[str] = None
        self._proposed_parameters: Dict[str, Any] = {}
        self._target_evaluation_metric: str = "f1_score"
        self._predicted_metric_delta: float = 0.05
        self._estimated_confidence: float = 0.85
        self._risk_level: RiskLevel = RiskLevel.MEDIUM
        self._dependencies: List[str] = ["pandas", "scikit-learn"]
        self._expected_side_effects: List[str] = []
        self._assumptions: List[str] = []
        self._constraints: List[str] = []
        self._metadata: Dict[str, Any] = {}

    def with_id(self, hyp_id: str) -> "ScientificHypothesisBuilder":
        self._id = hyp_id
        return self

    def with_problem_id(self, problem_id: str) -> "ScientificHypothesisBuilder":
        self._problem_id = problem_id
        return self

    def with_statement(self, statement: str) -> "ScientificHypothesisBuilder":
        self._statement = statement
        return self

    def with_observation_summary(self, summary: str) -> "ScientificHypothesisBuilder":
        self._observation_summary = summary
        return self

    def with_causal_mechanism(self, mechanism: str) -> "ScientificHypothesisBuilder":
        self._causal_mechanism = mechanism
        return self

    def with_transformation_type(self, transformation_type: str) -> "ScientificHypothesisBuilder":
        self._transformation_type = transformation_type
        return self

    def with_target_column(self, target_column: Optional[str]) -> "ScientificHypothesisBuilder":
        self._target_column = target_column
        return self

    def with_proposed_parameters(self, parameters: Dict[str, Any]) -> "ScientificHypothesisBuilder":
        self._proposed_parameters = parameters
        return self

    def with_target_evaluation_metric(self, metric: str) -> "ScientificHypothesisBuilder":
        self._target_evaluation_metric = metric
        return self

    def with_predicted_metric_delta(self, delta: float) -> "ScientificHypothesisBuilder":
        self._predicted_metric_delta = delta
        return self

    def with_estimated_confidence(self, confidence: float) -> "ScientificHypothesisBuilder":
        self._estimated_confidence = confidence
        return self

    def with_risk_level(self, risk_level: RiskLevel) -> "ScientificHypothesisBuilder":
        self._risk_level = risk_level
        return self

    def with_dependencies(self, dependencies: List[str]) -> "ScientificHypothesisBuilder":
        self._dependencies = dependencies
        return self

    def with_expected_side_effects(self, side_effects: List[str]) -> "ScientificHypothesisBuilder":
        self._expected_side_effects = side_effects
        return self

    def with_assumptions(self, assumptions: List[str]) -> "ScientificHypothesisBuilder":
        self._assumptions = assumptions
        return self

    def with_constraints(self, constraints: List[str]) -> "ScientificHypothesisBuilder":
        self._constraints = constraints
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "ScientificHypothesisBuilder":
        self._metadata = metadata
        return self

    def build(self) -> ScientificHypothesis:
        """Validate required fields and return a ScientificHypothesis object."""
        if not self._id:
            raise ValueError("ScientificHypothesis 'id' is required")
        if not self._problem_id:
            raise ValueError("ScientificHypothesis 'problem_id' is required")
        if not self._statement:
            raise ValueError("ScientificHypothesis 'statement' is required")
        if not self._transformation_type:
            raise ValueError("ScientificHypothesis 'transformation_type' is required")

        hypothesis = ScientificHypothesis(
            id=self._id,
            problem_id=self._problem_id,
            statement=self._statement,
            observation_summary=self._observation_summary or "",
            causal_mechanism=self._causal_mechanism or "",
            transformation_type=self._transformation_type,
            target_column=self._target_column,
            proposed_parameters=self._proposed_parameters,
            target_evaluation_metric=self._target_evaluation_metric,
            predicted_metric_delta=self._predicted_metric_delta,
            estimated_confidence=self._estimated_confidence,
            risk_level=self._risk_level,
            dependencies=self._dependencies,
            expected_side_effects=self._expected_side_effects,
            assumptions=self._assumptions,
            constraints=self._constraints,
            metadata=self._metadata,
        )

        HypothesisValidator.validate(hypothesis)
        return hypothesis

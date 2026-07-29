"""
services/autoscientist/reasoning_builder.py — Fluent Builder Pattern for ReasoningTrace.

Provides a clean builder interface for instantiating validated ReasoningTrace objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.reasoning_models import ReasoningTrace, ScientificMemoryInterface
from services.autoscientist.reasoning_validator import ReasoningValidator


class ReasoningTraceBuilder:
    """
    Fluent Builder for constructing ReasoningTrace domain objects.
    """

    def __init__(self) -> None:
        self._id: Optional[str] = None
        self._problem_id: Optional[str] = None
        self._category: Optional[ObservationCategory] = None
        self._reasoning_summary: Optional[str] = None
        self._inferred_mechanism: Optional[str] = None
        self._supporting_evidence: Dict[str, Any] = {}
        self._recommended_transformation_class: Optional[str] = None
        self._confidence: float = 0.90
        self._assumptions: List[str] = []
        self._constraints: List[str] = []
        self._risks: List[str] = []
        self._memory_insights: Optional[ScientificMemoryInterface] = None

    def with_id(self, trace_id: str) -> "ReasoningTraceBuilder":
        self._id = trace_id
        return self

    def with_problem_id(self, problem_id: str) -> "ReasoningTraceBuilder":
        self._problem_id = problem_id
        return self

    def with_category(self, category: ObservationCategory) -> "ReasoningTraceBuilder":
        self._category = category
        return self

    def with_reasoning_summary(self, summary: str) -> "ReasoningTraceBuilder":
        self._reasoning_summary = summary
        return self

    def with_inferred_mechanism(self, mechanism: str) -> "ReasoningTraceBuilder":
        self._inferred_mechanism = mechanism
        return self

    def with_supporting_evidence(self, evidence: Dict[str, Any]) -> "ReasoningTraceBuilder":
        self._supporting_evidence = evidence
        return self

    def with_recommended_transformation_class(self, transform_class: str) -> "ReasoningTraceBuilder":
        self._recommended_transformation_class = transform_class
        return self

    def with_confidence(self, confidence: float) -> "ReasoningTraceBuilder":
        self._confidence = max(0.0, min(1.0, confidence))
        return self

    def with_assumptions(self, assumptions: List[str]) -> "ReasoningTraceBuilder":
        self._assumptions = assumptions
        return self

    def with_constraints(self, constraints: List[str]) -> "ReasoningTraceBuilder":
        self._constraints = constraints
        return self

    def with_risks(self, risks: List[str]) -> "ReasoningTraceBuilder":
        self._risks = risks
        return self

    def with_memory_insights(self, memory_insights: ScientificMemoryInterface) -> "ReasoningTraceBuilder":
        self._memory_insights = memory_insights
        return self

    def build(self) -> ReasoningTrace:
        """Validate required fields and return a ReasoningTrace object."""
        if not self._id:
            raise ValueError("ReasoningTrace 'id' is required")
        if not self._problem_id:
            raise ValueError("ReasoningTrace 'problem_id' is required")
        if not self._category:
            raise ValueError("ReasoningTrace 'category' is required")

        trace = ReasoningTrace(
            id=self._id,
            problem_id=self._problem_id,
            category=self._category,
            reasoning_summary=self._reasoning_summary or "",
            inferred_mechanism=self._inferred_mechanism or "",
            supporting_evidence=self._supporting_evidence,
            recommended_transformation_class=self._recommended_transformation_class or "",
            confidence=self._confidence,
            assumptions=self._assumptions,
            constraints=self._constraints,
            risks=self._risks,
            memory_insights=self._memory_insights,
        )

        ReasoningValidator.validate(trace)
        return trace

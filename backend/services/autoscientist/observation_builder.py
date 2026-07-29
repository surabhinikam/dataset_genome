"""
services/autoscientist/observation_builder.py — Fluent Builder Pattern for ScientificObservation.

Provides a clean, fluid interface for instantiating validated ScientificObservation objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.observation_constants import DEFAULT_CONFIDENCE, ObservationCategory
from services.autoscientist.observation_models import ScientificObservation


class ScientificObservationBuilder:
    """
    Fluent Builder for constructing ScientificObservation domain objects.
    """

    def __init__(self) -> None:
        self._id: Optional[str] = None
        self._category: Optional[ObservationCategory] = None
        self._title: Optional[str] = None
        self._summary: Optional[str] = None
        self._affected_columns: List[str] = []
        self._severity: float = 0.0
        self._confidence: float = DEFAULT_CONFIDENCE
        self._evidence: Dict[str, Any] = {}
        self._recommendations: List[str] = []
        self._metadata: Dict[str, Any] = {}

    def with_id(self, obs_id: str) -> "ScientificObservationBuilder":
        self._id = obs_id
        return self

    def with_category(self, category: ObservationCategory) -> "ScientificObservationBuilder":
        self._category = category
        return self

    def with_title(self, title: str) -> "ScientificObservationBuilder":
        self._title = title
        return self

    def with_summary(self, summary: str) -> "ScientificObservationBuilder":
        self._summary = summary
        return self

    def with_affected_columns(self, affected_columns: List[str]) -> "ScientificObservationBuilder":
        self._affected_columns = affected_columns
        return self

    def with_severity(self, severity: float) -> "ScientificObservationBuilder":
        self._severity = max(0.0, min(1.0, severity))
        return self

    def with_confidence(self, confidence: float) -> "ScientificObservationBuilder":
        self._confidence = max(0.0, min(1.0, confidence))
        return self

    def with_evidence(self, evidence: Dict[str, Any]) -> "ScientificObservationBuilder":
        self._evidence = evidence
        return self

    def with_recommendations(self, recommendations: List[str]) -> "ScientificObservationBuilder":
        self._recommendations = recommendations
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "ScientificObservationBuilder":
        self._metadata = metadata
        return self

    def build(self) -> ScientificObservation:
        """Validate required fields and return a ScientificObservation object."""
        if not self._id:
            raise ValueError("Observation 'id' is required")
        if not self._category:
            raise ValueError("Observation 'category' is required")
        if not self._title:
            raise ValueError("Observation 'title' is required")
        if not self._summary:
            raise ValueError("Observation 'summary' is required")

        return ScientificObservation(
            id=self._id,
            category=self._category,
            title=self._title,
            summary=self._summary,
            affected_columns=self._affected_columns,
            severity=self._severity,
            confidence=self._confidence,
            evidence=self._evidence,
            recommendations=self._recommendations,
            metadata=self._metadata,
        )

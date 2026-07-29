"""
backend/app/orchestrator/events.py — Orchestrator Event System.

Defines GenomeEventType, GenomeEvent payload, and EventEmitter pattern.
"""

from datetime import datetime
from enum import Enum
import logging
from typing import Any, Callable, Dict, List
from pydantic import BaseModel, Field, ConfigDict


class GenomeEventType(str, Enum):
    """Pipeline event types."""
    DatasetGenerated = "DatasetGenerated"
    DatasetAnalyzed = "DatasetAnalyzed"
    EvolutionCompleted = "EvolutionCompleted"
    AdaptiveCompleted = "AdaptiveCompleted"
    TrainingCompleted = "TrainingCompleted"
    PublicationCompleted = "PublicationCompleted"
    PipelineCompleted = "PipelineCompleted"
    PipelineFailed = "PipelineFailed"


class GenomeEvent(BaseModel):
    """Event payload emitted by EventEmitter."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    event_type: GenomeEventType = Field(..., description="Type of event emitted")
    execution_id: str = Field(..., description="Run execution ID")
    stage_name: str = Field(..., description="Name of completed stage")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event emission timestamp")


class EventEmitter:
    """
    Observer pattern Event Emitter for broadcasting orchestration events.
    """

    def __init__(self) -> None:
        self._listeners: List[Callable[[GenomeEvent], None]] = []

    def subscribe(self, listener: Callable[[GenomeEvent], None]) -> None:
        """Subscribe event listener callback."""
        self._listeners.append(listener)

    def emit(self, event: GenomeEvent) -> None:
        """Broadcast event payload to all subscribed listeners."""
        logging.getLogger("dataset_genome.orchestrator.events").info(
            f"Event Emitted: '{event.event_type.value}' for stage '{event.stage_name}' (Execution: {event.execution_id})"
        )
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as exc:
                logging.getLogger("dataset_genome.orchestrator.events").error(
                    f"Error in event listener for '{event.event_type.value}': {exc}"
                )

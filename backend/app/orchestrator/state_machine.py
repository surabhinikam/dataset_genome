"""
backend/app/orchestrator/state_machine.py — Execution State Machine.

Defines ExecutionState enum and ExecutionStateMachine for pipeline lifecycle transitions.
"""

from enum import Enum
import logging
from typing import List, Set

logger = logging.getLogger("dataset_genome.orchestrator.state_machine")


class ExecutionState(str, Enum):
    """Pipeline execution state enum."""
    INITIALIZED = "INITIALIZED"
    GENERATING = "GENERATING"
    ANALYZING = "ANALYZING"
    EVOLVING = "EVOLVING"
    OPTIMIZING = "OPTIMIZING"
    TRAINING = "TRAINING"
    PUBLISHING = "PUBLISHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExecutionStateMachine:
    """
    Manages valid state transitions during Dataset Genome orchestration.
    """

    ALLOWED_TRANSITIONS = {
        ExecutionState.INITIALIZED: {ExecutionState.GENERATING, ExecutionState.FAILED},
        ExecutionState.GENERATING: {ExecutionState.ANALYZING, ExecutionState.FAILED},
        ExecutionState.ANALYZING: {ExecutionState.EVOLVING, ExecutionState.FAILED},
        ExecutionState.EVOLVING: {ExecutionState.OPTIMIZING, ExecutionState.FAILED},
        ExecutionState.OPTIMIZING: {ExecutionState.TRAINING, ExecutionState.FAILED},
        ExecutionState.TRAINING: {ExecutionState.PUBLISHING, ExecutionState.FAILED},
        ExecutionState.PUBLISHING: {ExecutionState.COMPLETED, ExecutionState.FAILED},
        ExecutionState.COMPLETED: set(),
        ExecutionState.FAILED: {ExecutionState.INITIALIZED},  # Allow reset
    }

    def __init__(self, initial_state: ExecutionState = ExecutionState.INITIALIZED) -> None:
        self._current_state = initial_state
        self._state_history: List[ExecutionState] = [initial_state]

    @property
    def current_state(self) -> ExecutionState:
        return self._current_state

    @property
    def history(self) -> List[ExecutionState]:
        return self._state_history

    def transition_to(self, new_state: ExecutionState) -> None:
        """Transition pipeline to new state if valid."""
        allowed = self.ALLOWED_TRANSITIONS.get(self._current_state, set())
        if new_state not in allowed and new_state != ExecutionState.FAILED:
            raise ValueError(
                f"Invalid state transition: Cannot transition from '{self._current_state.value}' to '{new_state.value}'."
            )

        logger.info(f"StateMachine transition: '{self._current_state.value}' -> '{new_state.value}'.")
        self._current_state = new_state
        self._state_history.append(new_state)

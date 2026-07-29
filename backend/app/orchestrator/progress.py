"""
backend/app/orchestrator/progress.py — Progress Tracking Module.

Tracks pipeline progress percentage, stage completion, timing, and module lists.
"""

import time
from typing import List, Optional
from pydantic import BaseModel, Field

from app.orchestrator.state_machine import ExecutionState


class ProgressTracker(BaseModel):
    """
    Progress Tracking State.
    """
    current_stage: ExecutionState = Field(ExecutionState.INITIALIZED, description="Current execution state")
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Overall completion percentage [0..100]")
    execution_time_seconds: float = Field(0.0, ge=0.0, description="Elapsed execution time in seconds")
    completed_modules: List[str] = Field(default_factory=list, description="List of completed module names")
    failed_modules: List[str] = Field(default_factory=list, description="List of failed module names")

    _start_time: Optional[float] = None

    def start_timer(self) -> None:
        self._start_time = time.time()

    def stop_timer(self) -> None:
        if self._start_time:
            self.execution_time_seconds = round(time.time() - self._start_time, 2)

    def update_stage(self, stage: ExecutionState, percent: float, module_name: Optional[str] = None) -> None:
        """Update tracker state and progress percentage."""
        self.current_stage = stage
        self.progress_percentage = round(max(0.0, min(100.0, percent)), 1)
        if self._start_time:
            self.execution_time_seconds = round(time.time() - self._start_time, 2)

        if module_name and module_name not in self.completed_modules:
            self.completed_modules.append(module_name)

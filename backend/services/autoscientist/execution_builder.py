"""
services/autoscientist/execution_builder.py — Fluent Builder Pattern for ExecutionResult.

Provides a fluid interface for constructing validated ExecutionResult domain objects.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.execution_models import ExecutionResult, ExecutionStatus


class ExecutionResultBuilder:
    """
    Fluent Builder for constructing ExecutionResult domain objects.
    """

    def __init__(self) -> None:
        self._execution_id: Optional[str] = None
        self._plan_id: Optional[str] = None
        self._status: ExecutionStatus = ExecutionStatus.COMPLETED
        self._dataset_version: str = "v1.1.0"
        self._output_dataset_path: str = ""
        self._execution_time_ms: float = 0.0
        self._memory_usage_mb: float = 0.0
        self._rows_before: int = 0
        self._rows_after: int = 0
        self._columns_before: int = 0
        self._columns_after: int = 0
        self._logs: List[str] = []
        self._warnings: List[str] = []
        self._errors: List[str] = []
        self._metadata: Dict[str, Any] = {}

    def with_execution_id(self, execution_id: str) -> "ExecutionResultBuilder":
        self._execution_id = execution_id
        return self

    def with_plan_id(self, plan_id: str) -> "ExecutionResultBuilder":
        self._plan_id = plan_id
        return self

    def with_status(self, status: ExecutionStatus) -> "ExecutionResultBuilder":
        self._status = status
        return self

    def with_dataset_version(self, dataset_version: str) -> "ExecutionResultBuilder":
        self._dataset_version = dataset_version
        return self

    def with_output_dataset_path(self, path: str) -> "ExecutionResultBuilder":
        self._output_dataset_path = path
        return self

    def with_execution_time_ms(self, time_ms: float) -> "ExecutionResultBuilder":
        self._execution_time_ms = max(0.0, time_ms)
        return self

    def with_memory_usage_mb(self, memory_mb: float) -> "ExecutionResultBuilder":
        self._memory_usage_mb = max(0.0, memory_mb)
        return self

    def with_rows_before(self, count: int) -> "ExecutionResultBuilder":
        self._rows_before = max(0, count)
        return self

    def with_rows_after(self, count: int) -> "ExecutionResultBuilder":
        self._rows_after = max(0, count)
        return self

    def with_columns_before(self, count: int) -> "ExecutionResultBuilder":
        self._columns_before = max(0, count)
        return self

    def with_columns_after(self, count: int) -> "ExecutionResultBuilder":
        self._columns_after = max(0, count)
        return self

    def with_logs(self, logs: List[str]) -> "ExecutionResultBuilder":
        self._logs = logs
        return self

    def with_warnings(self, warnings: List[str]) -> "ExecutionResultBuilder":
        self._warnings = warnings
        return self

    def with_errors(self, errors: List[str]) -> "ExecutionResultBuilder":
        self._errors = errors
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "ExecutionResultBuilder":
        self._metadata = metadata
        return self

    def build(self) -> ExecutionResult:
        """Validate required fields and return an ExecutionResult object."""
        if not self._execution_id:
            raise ValueError("ExecutionResult 'execution_id' is required")
        if not self._plan_id:
            raise ValueError("ExecutionResult 'plan_id' is required")

        return ExecutionResult(
            execution_id=self._execution_id,
            plan_id=self._plan_id,
            status=self._status,
            dataset_version=self._dataset_version,
            output_dataset_path=self._output_dataset_path,
            execution_time_ms=self._execution_time_ms,
            memory_usage_mb=self._memory_usage_mb,
            rows_before=self._rows_before,
            rows_after=self._rows_after,
            columns_before=self._columns_before,
            columns_after=self._columns_after,
            logs=self._logs,
            warnings=self._warnings,
            errors=self._errors,
            metadata=self._metadata,
        )

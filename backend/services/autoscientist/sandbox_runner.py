"""
services/autoscientist/sandbox_runner.py — Sandboxed Execution Runner.

Provides an in-memory execution sandbox measuring runtime milliseconds, peak RAM usage (MB),
capturing logs and warnings, and catching runtime exceptions cleanly without shell execution.
"""

import time
import tracemalloc
from typing import Any, Dict, List, Tuple
import pandas as pd

from services.autoscientist.transformations.base import BaseTransformation


class SandboxExecutionResult:
    """Container holding in-memory sandbox execution metrics and output DataFrame."""
    def __init__(
        self,
        transformed_df: pd.DataFrame,
        execution_time_ms: float,
        memory_usage_mb: float,
        logs: List[str],
        warnings: List[str],
        errors: List[str]
    ):
        self.transformed_df = transformed_df
        self.execution_time_ms = execution_time_ms
        self.memory_usage_mb = memory_usage_mb
        self.logs = logs
        self.warnings = warnings
        self.errors = errors


class SandboxedExecutionRunner:
    """
    Isolated In-Memory Execution Sandbox for Dataset Transformations.
    """

    @classmethod
    def execute_in_sandbox(
        cls,
        transformation: BaseTransformation,
        df: pd.DataFrame,
        parameters: Dict[str, Any],
        target_columns: List[str]
    ) -> SandboxExecutionResult:
        """
        Execute transformation in isolated sandbox, capturing time, memory, logs, warnings, and errors.
        """
        logs: List[str] = [f"Started sandboxed execution for '{transformation.name}'."]
        warnings: List[str] = []
        errors: List[str] = []

        # Start memory and time tracking
        tracemalloc.start()
        start_time = time.perf_counter()

        transformed_df = df.copy()

        try:
            res_df, res_logs, res_warnings = transformation.transform(df, parameters, target_columns)
            transformed_df = res_df
            logs.extend(res_logs)
            warnings.extend(res_warnings)
        except Exception as e:
            err_msg = f"Transformation '{transformation.name}' failed with error: {str(e)}"
            errors.append(err_msg)
            logs.append(err_msg)

        # Stop time and memory tracking
        end_time = time.perf_counter()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        execution_time_ms = round((end_time - start_time) * 1000.0, 2)
        memory_usage_mb = round(peak_mem / (1024.0 * 1024.0), 4)

        logs.append(f"Completed sandbox run in {execution_time_ms:.2f} ms (Peak RAM: {memory_usage_mb:.4f} MB).")

        return SandboxExecutionResult(
            transformed_df=transformed_df,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=memory_usage_mb,
            logs=logs,
            warnings=warnings,
            errors=errors
        )

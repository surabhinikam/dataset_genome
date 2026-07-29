"""
services/autoscientist/execution_result.py — Execution Result Module.

Re-exports ExecutionResult and provides helper methods for formatting execution reports.
"""

from services.autoscientist.execution_models import ExecutionResult, ExecutionStatus

__all__ = ["ExecutionResult", "ExecutionStatus"]

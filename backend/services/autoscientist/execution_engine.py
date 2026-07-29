"""
services/autoscientist/execution_engine.py — Main Execution Engine Coordinator.

Executes approved experiment plans in an isolated sandbox, manages dataset lineage versioning,
and produces ExecutionResult objects.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

from core.config import settings
from services.autoscientist.execution_builder import ExecutionResultBuilder
from services.autoscientist.execution_models import ExecutionResult, ExecutionStatus
from services.autoscientist.execution_validator import ExecutionValidator
from services.autoscientist.experiment_models import ExperimentPlan
from services.autoscientist.sandbox_runner import SandboxedExecutionRunner
from services.autoscientist.transformation_registry import TransformationRegistry

logger = logging.getLogger("dataset_genome.execution_engine")


class ExecutionEngine:
    """
    Core Execution Engine for Dataset Genome AutoScientist.
    
    Transforms datasets by executing approved ExperimentPlan objects in a sandboxed runner.
    """

    def __init__(self) -> None:
        self._registry = TransformationRegistry()
        self._validator = ExecutionValidator()

    def execute_plan(
        self,
        plan: ExperimentPlan,
        df: pd.DataFrame,
        dataset_id: Optional[uuid.UUID] = None,
        source_filename: str = "dataset.csv"
    ) -> ExecutionResult:
        """
        Execute an approved ExperimentPlan on a pandas DataFrame.
        """
        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        logger.info(f"Starting execution '{execution_id}' for plan_id='{plan.plan_id}'")

        rows_before, cols_before = len(df), len(df.columns)

        # 1. Pre-execution Validation
        try:
            self._validator.validate_pre_execution(plan, df)
        except Exception as e:
            logger.error(f"Pre-execution validation failed: {str(e)}")
            return (
                ExecutionResultBuilder()
                .with_execution_id(execution_id)
                .with_plan_id(plan.plan_id)
                .with_status(ExecutionStatus.REJECTED)
                .with_dataset_version(plan.expected_dataset_version)
                .with_output_dataset_path("")
                .with_rows_before(rows_before)
                .with_rows_after(rows_before)
                .with_columns_before(cols_before)
                .with_columns_after(cols_before)
                .with_errors([f"Pre-execution validation failed: {str(e)}"])
                .build()
            )

        # 2. Get Transformation Plugin from Registry
        try:
            transformation = self._registry.get(plan.transformation_type)
        except Exception as e:
            logger.error(f"Transformation lookup failed: {str(e)}")
            return (
                ExecutionResultBuilder()
                .with_execution_id(execution_id)
                .with_plan_id(plan.plan_id)
                .with_status(ExecutionStatus.FAILED)
                .with_dataset_version(plan.expected_dataset_version)
                .with_output_dataset_path("")
                .with_rows_before(rows_before)
                .with_rows_after(rows_before)
                .with_columns_before(cols_before)
                .with_columns_after(cols_before)
                .with_errors([str(e)])
                .build()
            )

        # 3. Execute Transformation in Sandboxed Runner
        sandbox_res = SandboxedExecutionRunner.execute_in_sandbox(
            transformation=transformation,
            df=df,
            parameters=plan.parameters,
            target_columns=plan.target_columns,
        )

        if sandbox_res.errors:
            return (
                ExecutionResultBuilder()
                .with_execution_id(execution_id)
                .with_plan_id(plan.plan_id)
                .with_status(ExecutionStatus.FAILED)
                .with_dataset_version(plan.expected_dataset_version)
                .with_output_dataset_path("")
                .with_execution_time_ms(sandbox_res.execution_time_ms)
                .with_memory_usage_mb(sandbox_res.memory_usage_mb)
                .with_rows_before(rows_before)
                .with_rows_after(rows_before)
                .with_columns_before(cols_before)
                .with_columns_after(cols_before)
                .with_logs(sandbox_res.logs)
                .with_warnings(sandbox_res.warnings)
                .with_errors(sandbox_res.errors)
                .build()
            )

        transformed_df = sandbox_res.transformed_df
        rows_after, cols_after = len(transformed_df), len(transformed_df.columns)

        # 4. Post-execution Validation
        try:
            self._validator.validate_post_execution(df, transformed_df, plan)
        except Exception as e:
            logger.error(f"Post-execution validation failed: {str(e)}")
            return (
                ExecutionResultBuilder()
                .with_execution_id(execution_id)
                .with_plan_id(plan.plan_id)
                .with_status(ExecutionStatus.FAILED)
                .with_dataset_version(plan.expected_dataset_version)
                .with_output_dataset_path("")
                .with_execution_time_ms(sandbox_res.execution_time_ms)
                .with_memory_usage_mb(sandbox_res.memory_usage_mb)
                .with_rows_before(rows_before)
                .with_rows_after(rows_after)
                .with_columns_before(cols_before)
                .with_columns_after(cols_after)
                .with_logs(sandbox_res.logs)
                .with_warnings(sandbox_res.warnings)
                .with_errors([f"Post-execution validation failed: {str(e)}"])
                .build()
            )

        # 5. Save Transformed Dataset into Versioned Path
        new_version_tag = plan.expected_dataset_version or "v1.1.0"
        dataset_uuid = dataset_id or uuid.uuid4()
        clean_name = Path(source_filename).stem
        versioned_filename = f"{dataset_uuid}_{new_version_tag}_{clean_name}.csv"
        
        output_dir = settings.upload_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / versioned_filename

        transformed_df.to_csv(output_path, index=False)
        sandbox_res.logs.append(f"Saved versioned transformed dataset ({rows_after:,} rows, {cols_after} cols) to '{output_path}'.")

        return (
            ExecutionResultBuilder()
            .with_execution_id(execution_id)
            .with_plan_id(plan.plan_id)
            .with_status(ExecutionStatus.COMPLETED)
            .with_dataset_version(new_version_tag)
            .with_output_dataset_path(str(output_path))
            .with_execution_time_ms(sandbox_res.execution_time_ms)
            .with_memory_usage_mb(sandbox_res.memory_usage_mb)
            .with_rows_before(rows_before)
            .with_rows_after(rows_after)
            .with_columns_before(cols_before)
            .with_columns_after(cols_after)
            .with_logs(sandbox_res.logs)
            .with_warnings(sandbox_res.warnings)
            .with_errors([])
            .with_metadata({"output_filename": versioned_filename})
            .build()
        )

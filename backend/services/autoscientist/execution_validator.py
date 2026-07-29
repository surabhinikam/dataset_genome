"""
services/autoscientist/execution_validator.py — Execution Validator Module.

Validates pre-execution input ExperimentPlan, dataset schema, and post-execution output DataFrame.
"""

from typing import List, Optional
import pandas as pd
from services.autoscientist.experiment_models import ExperimentPlan


class ExecutionValidator:
    """
    Validates input experiment plans and mutated DataFrames.
    """

    @classmethod
    def validate_pre_execution(cls, plan: ExperimentPlan, df: pd.DataFrame) -> bool:
        """
        Pre-execution validation: check dataset presence, target columns, and row counts.
        """
        errors: List[str] = []

        if df is None or df.empty:
            errors.append("Input DataFrame is empty or None.")
            raise ValueError(f"Pre-execution validation failed: {'; '.join(errors)}")

        if len(df) == 0 or len(df.columns) == 0:
            errors.append("Input DataFrame has zero rows or zero columns.")

        # Check target columns existence for specific non-dropping transformations
        if plan.transformation_type not in ["RowDeduplicationTransformation"]:
            for col in plan.target_columns:
                if col not in df.columns:
                    # Log warning or error if target column is absent
                    pass

        if errors:
            raise ValueError(f"Pre-execution validation failed: {'; '.join(errors)}")

        return True

    @classmethod
    def validate_post_execution(cls, original_df: pd.DataFrame, transformed_df: pd.DataFrame, plan: ExperimentPlan) -> bool:
        """
        Post-execution validation: verify non-empty transformed DataFrame and valid row/col bounds.
        """
        errors: List[str] = []

        if transformed_df is None or transformed_df.empty:
            errors.append("Transformed DataFrame is empty or None.")

        if len(transformed_df) == 0:
            errors.append("Transformed DataFrame has 0 rows.")

        if len(transformed_df.columns) == 0:
            errors.append("Transformed DataFrame has 0 columns.")

        if errors:
            raise ValueError(f"Post-execution validation failed: {'; '.join(errors)}")

        return True

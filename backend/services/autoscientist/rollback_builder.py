"""
services/autoscientist/rollback_builder.py — Rollback Plan Builder.

Generates automated rollback procedures and steps for reverting dataset experiment mutations.
"""

from typing import List, Optional
from services.autoscientist.experiment_models import ExecutionStep, RollbackPlan


class RollbackPlanBuilder:
    """
    Generates automated rollback strategies for dataset experiments.
    """

    @classmethod
    def build_rollback_plan(
        cls,
        transformation_type: str,
        target_columns: List[str],
        parent_version: str = "v1.0.0"
    ) -> RollbackPlan:
        """Construct automated RollbackPlan."""
        target_str = ", ".join([f"'{c}'" for c in target_columns]) or "dataset"

        if transformation_type == "FeatureDropTransformation":
            steps = [
                ExecutionStep(
                    step_number=1,
                    action="LOAD_BASELINE_SNAPSHOT",
                    target=parent_version,
                    parameters={"parent_version": parent_version},
                    description=f"Load parent baseline dataset version snapshot '{parent_version}'."
                ),
                ExecutionStep(
                    step_number=2,
                    action="RESTORE_DROPPED_COLUMNS",
                    target=target_str,
                    parameters={"columns": target_columns},
                    description=f"Re-attach dropped column(s) {target_str} to dataset schema."
                ),
                ExecutionStep(
                    step_number=3,
                    action="VERIFY_SCHEMA_INTEGRITY",
                    target=target_str,
                    parameters={},
                    description="Verify schema column alignment against baseline."
                )
            ]
            desc = f"Automated rollback strategy to restore dropped column(s) {target_str} from parent version '{parent_version}'."

        elif transformation_type in ["ImputationTransformation", "MedianImputationTransformation"]:
            steps = [
                ExecutionStep(
                    step_number=1,
                    action="LOAD_NULL_MASK_BACKUP",
                    target=target_str,
                    parameters={"parent_version": parent_version},
                    description=f"Load baseline null value mask for column(s) {target_str}."
                ),
                ExecutionStep(
                    step_number=2,
                    action="REVERT_IMPUTED_VALUES",
                    target=target_str,
                    parameters={"columns": target_columns},
                    description=f"Revert imputed synthetic values back to null values in column(s) {target_str}."
                )
            ]
            desc = f"Automated rollback strategy to restore original null mask in column(s) {target_str}."

        elif transformation_type == "WinsorizationTransformation":
            steps = [
                ExecutionStep(
                    step_number=1,
                    action="RESTORE_RAW_VALUES",
                    target=target_str,
                    parameters={"parent_version": parent_version, "columns": target_columns},
                    description=f"Restore uncapped raw numeric values for column(s) {target_str} from baseline."
                )
            ]
            desc = f"Automated rollback strategy to restore raw outlier values for column(s) {target_str}."

        elif transformation_type == "ClassRebalancingTransformation":
            steps = [
                ExecutionStep(
                    step_number=1,
                    action="DROP_SYNTHETIC_ROWS",
                    target=target_str,
                    parameters={"parent_version": parent_version},
                    description="Remove synthetically generated SMOTE oversampled rows."
                ),
                ExecutionStep(
                    step_number=2,
                    action="RESTORE_ORIGINAL_ROW_COUNT",
                    target=parent_version,
                    parameters={},
                    description=f"Restore original baseline row count from version '{parent_version}'."
                )
            ]
            desc = "Automated rollback strategy to prune synthetic oversampled rows."

        else:
            steps = [
                ExecutionStep(
                    step_number=1,
                    action="RESTORE_BASELINE_VERSION",
                    target=parent_version,
                    parameters={"parent_version": parent_version},
                    description=f"Revert dataset pointer back to baseline parent version '{parent_version}'."
                )
            ]
            desc = f"Automated fallback rollback strategy restoring parent dataset version '{parent_version}'."

        return RollbackPlan(
            is_supported=True,
            rollback_strategy=f"ROLLBACK_{transformation_type.upper()}",
            rollback_steps=steps,
            backup_required=True,
            description=desc,
        )

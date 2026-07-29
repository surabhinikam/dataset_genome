"""
services/autoscientist/validation_rules.py — Validation Rule Generator.

Generates pre-mutation and post-mutation validation checklists ensuring target column existence,
dtype compatibility, schema alignment, and zero target leakage.
"""

from typing import List
from services.autoscientist.experiment_models import ValidationRuleItem


class ValidationRuleGenerator:
    """
    Generates structured validation checklists for ExperimentPlans.
    """

    @classmethod
    def generate_rules(
        cls,
        transformation_type: str,
        target_columns: List[str]
    ) -> List[ValidationRuleItem]:
        """Generate validation rule checklist items."""
        rules: List[ValidationRuleItem] = []
        target_str = ", ".join([f"'{c}'" for c in target_columns]) or "dataset"

        # 1. Universal Pre-Execution Rule: Column Existence
        rules.append(
            ValidationRuleItem(
                rule_id="val-col-exists",
                rule_name="Target Column Existence Check",
                target=target_str,
                check="COLUMN_EXISTS",
                description=f"Verify target column(s) {target_str} exist in dataset schema."
            )
        )

        # 2. Universal Pre-Execution Rule: Target Leakage Check
        rules.append(
            ValidationRuleItem(
                rule_id="val-no-target-leakage",
                rule_name="No Target Leakage Safety Check",
                target=target_str,
                check="NO_TARGET_LEAKAGE",
                description="Verify target prediction label column is not accidentally dropped or mutated."
            )
        )

        # 3. Category-Specific Validation Rules
        if transformation_type == "FeatureDropTransformation":
            rules.append(
                ValidationRuleItem(
                    rule_id="val-non-empty-remainder",
                    rule_name="Non-Empty Remainder Features Check",
                    target="schema",
                    check="MIN_FEATURES_REMAIN",
                    description="Verify dataset retains at least 1 predictive feature column after drop."
                )
            )

        elif transformation_type in ["ImputationTransformation", "MedianImputationTransformation"]:
            rules.append(
                ValidationRuleItem(
                    rule_id="val-zero-nulls-post",
                    rule_name="Post-Imputation Zero Null Check",
                    target=target_str,
                    check="ZERO_NULL_COUNT",
                    description=f"Verify target column(s) {target_str} contain 0 missing cells post-imputation."
                )
            )

        elif transformation_type == "WinsorizationTransformation":
            rules.append(
                ValidationRuleItem(
                    rule_id="val-bounded-quantiles",
                    rule_name="Post-Winsorization Bounds Check",
                    target=target_str,
                    check="BOUNDED_QUANTILES",
                    description=f"Verify feature {target_str} values lie strictly within 1st-99th percentile bounds."
                )
            )

        elif transformation_type == "ClassRebalancingTransformation":
            rules.append(
                ValidationRuleItem(
                    rule_id="val-balanced-class-ratio",
                    rule_name="Post-SMOTE Class Equilibrium Check",
                    target=target_str,
                    check="BALANCED_CLASS_RATIO",
                    description=f"Verify target feature {target_str} majority class ratio is reduced below 85%."
                )
            )

        # 4. Universal Post-Execution Rule: Non-Empty DataFrame
        rules.append(
            ValidationRuleItem(
                rule_id="val-non-empty-df",
                rule_name="Non-Empty Dataset Row Count Check",
                target="dataframe",
                check="ROW_COUNT_GREATER_THAN_ZERO",
                description="Verify mutated dataset contains > 0 rows."
            )
        )

        return rules

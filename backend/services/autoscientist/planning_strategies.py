"""
services/autoscientist/planning_strategies.py — Planning Strategy Classes (Strategy Pattern).

Implements independent planning strategies for KNN Imputation, Median Imputation,
Feature Drop, Winsorization, SMOTE Class Rebalancing, and Feature Pruning.
"""

from typing import Any, Dict, List
from services.autoscientist.experiment_models import ExecutionStep, ResourceEstimate, RollbackPlan, ValidationRuleItem
from services.autoscientist.hypothesis_models import ScientificHypothesis
from services.autoscientist.resource_estimator import ResourceEstimator
from services.autoscientist.rollback_builder import RollbackPlanBuilder
from services.autoscientist.validation_rules import ValidationRuleGenerator


class StrategyResult:
    """Container for planning outputs produced by a BasePlanningStrategy."""
    def __init__(
        self,
        execution_steps: List[ExecutionStep],
        validation_rules: List[ValidationRuleItem],
        rollback_plan: RollbackPlan,
        resource_estimate: ResourceEstimate,
        target_columns: List[str]
    ):
        self.execution_steps = execution_steps
        self.validation_rules = validation_rules
        self.rollback_plan = rollback_plan
        self.resource_estimate = resource_estimate
        self.target_columns = target_columns


class BasePlanningStrategy:
    """Base interface for transformation planning strategies."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        raise NotImplementedError


class FeatureDropPlanningStrategy(BasePlanningStrategy):
    """Planning strategy for FeatureDropTransformation."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        params = hypothesis.proposed_parameters
        drop_cols = params.get("drop_columns") or ([hypothesis.target_column] if hypothesis.target_column else ["constant_col"])
        cols_str = ", ".join([f"'{c}'" for c in drop_cols])

        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="VALIDATE_PRE_MUTATION",
                target=cols_str,
                parameters={"rule_check": "COLUMN_EXISTS"},
                description=f"Validate that target feature column(s) {cols_str} exist in schema."
            ),
            ExecutionStep(
                step_number=3,
                action="DROP_FEATURE_COLUMNS",
                target=cols_str,
                parameters={"drop_columns": drop_cols},
                description=f"Execute pandas.DataFrame.drop(columns={drop_cols}) to remove feature(s)."
            ),
            ExecutionStep(
                step_number=4,
                action="EXPORT_VERSIONED_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Export transformed dataset to new versioned artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, drop_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, drop_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=params)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=drop_cols
        )


class ImputationPlanningStrategy(BasePlanningStrategy):
    """Planning strategy for ImputationTransformation (KNN Imputer)."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        params = hypothesis.proposed_parameters
        target_cols = [hypothesis.target_column] if hypothesis.target_column else ["imputed_col"]
        cols_str = ", ".join([f"'{c}'" for c in target_cols])
        n_neighbors = params.get("n_neighbors", 5)

        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="RECORD_NULL_MASK",
                target=cols_str,
                parameters={"columns": target_cols},
                description=f"Record baseline null mask for column(s) {cols_str} for rollback tracking."
            ),
            ExecutionStep(
                step_number=3,
                action="APPLY_KNN_IMPUTATION",
                target=cols_str,
                parameters={"n_neighbors": n_neighbors, "columns": target_cols},
                description=f"Fit and transform sklearn.impute.KNNImputer(n_neighbors={n_neighbors}) on column(s) {cols_str}."
            ),
            ExecutionStep(
                step_number=4,
                action="EXPORT_VERSIONED_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Export transformed dataset to new versioned artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, target_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, target_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=params)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=target_cols
        )


class WinsorizationPlanningStrategy(BasePlanningStrategy):
    """Planning strategy for WinsorizationTransformation."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        params = hypothesis.proposed_parameters
        target_cols = [hypothesis.target_column] if hypothesis.target_column else ["numeric_col"]
        cols_str = ", ".join([f"'{c}'" for c in target_cols])
        lower_q = params.get("lower_quantile", 0.01)
        upper_q = params.get("upper_quantile", 0.99)

        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="COMPUTE_QUANTILE_BOUNDS",
                target=cols_str,
                parameters={"lower_quantile": lower_q, "upper_quantile": upper_q},
                description=f"Compute {lower_q:.0%} and {upper_q:.0%} quantile bounds for column(s) {cols_str}."
            ),
            ExecutionStep(
                step_number=3,
                action="APPLY_QUANTILE_CLIPPING",
                target=cols_str,
                parameters={"lower_quantile": lower_q, "upper_quantile": upper_q},
                description=f"Execute pandas.Series.clip() to cap outliers outside [{lower_q}, {upper_q}] bounds."
            ),
            ExecutionStep(
                step_number=4,
                action="EXPORT_VERSIONED_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Export transformed dataset to new versioned artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, target_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, target_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=params)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=target_cols
        )


class ClassRebalancingPlanningStrategy(BasePlanningStrategy):
    """Planning strategy for ClassRebalancingTransformation (SMOTE)."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        params = hypothesis.proposed_parameters
        target_cols = [hypothesis.target_column] if hypothesis.target_column else ["target_col"]
        cols_str = ", ".join([f"'{c}'" for c in target_cols])
        strategy = params.get("sampling_strategy", "auto")

        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="SEPARATE_FEATURES_AND_TARGET",
                target=cols_str,
                parameters={"target_column": target_cols[0]},
                description=f"Separate feature matrix X and target label vector y ('{target_cols[0]}')."
            ),
            ExecutionStep(
                step_number=3,
                action="APPLY_SMOTE_OVERSAMPLING",
                target=cols_str,
                parameters={"sampling_strategy": strategy},
                description=f"Fit and resample imblearn.over_sampling.SMOTE(sampling_strategy='{strategy}') on minority classes."
            ),
            ExecutionStep(
                step_number=4,
                action="RECONSTRUCT_AND_EXPORT_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Re-combine resampled X and y into versioned dataset artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, target_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, target_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=params)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=target_cols
        )


class FeaturePruningPlanningStrategy(BasePlanningStrategy):
    """Planning strategy for FeaturePruningTransformation (Correlation Reduction)."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        params = hypothesis.proposed_parameters
        prune_col = params.get("prune_column") or hypothesis.target_column or "col_b"
        retain_col = params.get("retain_column", "col_a")
        target_cols = [prune_col]

        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="VERIFY_CORRELATION_PAIR",
                target=f"'{retain_col}' & '{prune_col}'",
                parameters={"retain": retain_col, "prune": prune_col},
                description=f"Verify pairwise linear correlation between '{retain_col}' and '{prune_col}'."
            ),
            ExecutionStep(
                step_number=3,
                action="PRUNE_REDUNDANT_FEATURE",
                target=prune_col,
                parameters={"drop_columns": [prune_col]},
                description=f"Drop redundant feature '{prune_col}' while retaining '{retain_col}'."
            ),
            ExecutionStep(
                step_number=4,
                action="EXPORT_VERSIONED_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Export transformed dataset to new versioned artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, target_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, target_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=params)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=target_cols
        )


class FallbackPlanningStrategy(BasePlanningStrategy):
    """Fallback strategy for custom or unrecognized transformation classes."""

    def plan(self, hypothesis: ScientificHypothesis) -> StrategyResult:
        target_cols = [hypothesis.target_column] if hypothesis.target_column else ["target_col"]
        steps = [
            ExecutionStep(
                step_number=1,
                action="LOAD_DATASET_CSV",
                target="dataset.csv",
                parameters={},
                description="Load current dataset version into memory."
            ),
            ExecutionStep(
                step_number=2,
                action="APPLY_GENERIC_MUTATION",
                target=hypothesis.transformation_type,
                parameters=hypothesis.proposed_parameters,
                description=f"Apply generic dataset transformation '{hypothesis.transformation_type}'."
            ),
            ExecutionStep(
                step_number=3,
                action="EXPORT_VERSIONED_CSV",
                target="v1.1.0",
                parameters={"version": "v1.1.0"},
                description="Export transformed dataset to new versioned artifact storage."
            )
        ]

        rules = ValidationRuleGenerator.generate_rules(hypothesis.transformation_type, target_cols)
        rollback = RollbackPlanBuilder.build_rollback_plan(hypothesis.transformation_type, target_cols)
        resources = ResourceEstimator.estimate_resources(hypothesis.transformation_type, parameters=hypothesis.proposed_parameters)

        return StrategyResult(
            execution_steps=steps,
            validation_rules=rules,
            rollback_plan=rollback,
            resource_estimate=resources,
            target_columns=target_cols
        )


# Strategy Registry
PLANNING_STRATEGY_REGISTRY: Dict[str, BasePlanningStrategy] = {
    "FeatureDropTransformation": FeatureDropPlanningStrategy(),
    "ImputationTransformation": ImputationPlanningStrategy(),
    "MedianImputationTransformation": ImputationPlanningStrategy(),
    "WinsorizationTransformation": WinsorizationPlanningStrategy(),
    "ClassRebalancingTransformation": ClassRebalancingPlanningStrategy(),
    "FeaturePruningTransformation": FeaturePruningPlanningStrategy(),
}

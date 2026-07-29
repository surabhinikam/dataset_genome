"""
services/autoscientist/reasoning_templates.py — Template-Based Scientific Reasoning.

Provides deterministic, explainable causal reasoning logic for all 6 dataset profiler categories:
Completeness, Correlation, Balance, Noise, Consistency, and Feature Quality.
"""

from typing import Dict, List, Tuple
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.ranking_models import RankedProblem
from services.autoscientist.reasoning_constants import DEFAULT_SYSTEM_CONSTRAINTS, TransformationClass


class ReasoningTemplateResult:
    """Structured container holding template output fields for ReasoningTrace assembly."""
    def __init__(
        self,
        reasoning_summary: str,
        inferred_mechanism: str,
        recommended_transformation_class: str,
        confidence: float,
        assumptions: List[str],
        constraints: List[str],
        risks: List[str]
    ):
        self.reasoning_summary = reasoning_summary
        self.inferred_mechanism = inferred_mechanism
        self.recommended_transformation_class = recommended_transformation_class
        self.confidence = confidence
        self.assumptions = assumptions
        self.constraints = constraints
        self.risks = risks


class BaseReasoningTemplate:
    """Base interface for category-specific reasoning templates."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        raise NotImplementedError


class CompletenessReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Completeness flaws (missing cell data)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
        missing_rate = obs.evidence.get("missing_rate") or obs.evidence.get("missing_cell_ratio", 0.10)

        if missing_rate > 0.50:
            transform_class = TransformationClass.FEATURE_DROP.value
            mechanism = f"Severe missingness mechanism (Missing Not at Random - MNAR, missing rate = {missing_rate:.1%})."
            summary = (
                f"Column(s) {cols} exhibit severe missingness exceeding 50%. "
                f"Imputing over 50% missing values introduces excessive synthetic noise. "
                f"Dropping column(s) {cols} is the optimal transformation strategy."
            )
            assumptions = ["Imputing > 50% missing values introduces model distortion."]
            risks = ["Loss of potentially predictive signal contained in non-null rows."]
        else:
            transform_class = TransformationClass.IMPUTATION.value
            mechanism = f"Moderate missingness mechanism (Missing Completely at Random - MCAR / MAR, missing rate = {missing_rate:.1%})."
            summary = (
                f"Column(s) {cols} contain moderate missing data ({missing_rate:.1%}). "
                f"Applying KNN or median/mode statistical imputation restores dataset completeness "
                f"without distorting underlying distribution parameters."
            )
            assumptions = ["Missing values are Missing at Random (MAR) or Missing Completely at Random (MCAR)."]
            risks = ["Minor attenuation of feature variance if unvaried median/mode imputation is applied."]

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.92,
            assumptions=assumptions,
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=risks
        )


class CorrelationReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Correlation flaws (multicollinearity)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        pair_cols = " & ".join([f"'{c}'" for c in obs.affected_columns])
        pearson_coeff = obs.evidence.get("pearson_coefficient", 0.90)

        transform_class = TransformationClass.FEATURE_PRUNING.value
        mechanism = f"Severe pairwise linear multicollinearity (|r| = {abs(pearson_coeff):.2f} >= 0.85)."
        summary = (
            f"Features {pair_cols} exhibit extreme linear correlation (Pearson r = {pearson_coeff:+.2f}). "
            f"Retaining both collinear dimensions causes matrix ill-conditioning and inflates feature variance. "
            f"Pruning the redundant dimension eliminates structural colinearity."
        )

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.95,
            assumptions=["The two correlated features share redundant predictive information."],
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=["Minor loss of non-linear signal if one feature carries subtle unique interactions."]
        )


class BalanceReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Balance flaws (class imbalance)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
        maj_ratio = obs.evidence.get("majority_class_ratio", 0.85)

        transform_class = TransformationClass.CLASS_REBALANCING.value
        mechanism = f"Categorical class distribution skewness (Majority class ratio = {maj_ratio:.1%})."
        summary = (
            f"Categorical feature/target {cols} suffers from severe class imbalance ({maj_ratio:.1%} majority class). "
            f"Unbalanced training data biases classifiers towards majority class prediction. "
            f"Applying synthetic oversampling (SMOTE) or adaptive resampling restores class equilibrium."
        )

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.88,
            assumptions=["Synthetic oversampling generates valid feature space interpolation."],
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=["Potential over-fitting if SMOTE oversamples noisy minority observations."]
        )


class NoiseReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Noise flaws (IQR outliers)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
        outlier_count = obs.evidence.get("outlier_count", 0)
        outlier_ratio = obs.evidence.get("outlier_ratio", 0.05)

        transform_class = TransformationClass.WINSORIZATION.value
        mechanism = f"Heavy-tailed extreme value noise corruption ({outlier_count:,} outliers, {outlier_ratio:.1%})."
        summary = (
            f"Numeric feature {cols} contains {outlier_count:,} statistical outliers ({outlier_ratio:.1%}) "
            f"outside IQR 1.5x boundaries. Extreme outliers corrupt mean/std scaling and destabilize loss gradients. "
            f"Applying 1%-99% Winsorization or quantile clipping bounds extreme noise while preserving sample size."
        )

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.90,
            assumptions=["Outliers represent measurement noise rather than true rare physical phenomena."],
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=["Truncation of extreme genuine domain events if bounds are set too narrow."]
        )


class ConsistencyReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Consistency flaws (duplicates & mixed types)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation

        if "duplicate" in obs.title.lower():
            transform_class = TransformationClass.ROW_DEDUPLICATION.value
            dup_rows = obs.evidence.get("duplicate_rows", 0)
            dup_ratio = obs.evidence.get("duplicate_ratio", 0.01)
            mechanism = f"Exact row duplication ({dup_rows:,} rows, {dup_ratio:.1%})."
            summary = (
                f"Dataset contains {dup_rows:,} exact duplicate rows ({dup_ratio:.1%}). "
                f"Duplicate rows inflate training sample size and risk severe train-test data leakage. "
                f"Deduplicating rows ensures clean empirical validation boundaries."
            )
            assumptions = ["Exact duplicate rows represent redundant data collection entries."]
            risks = ["None. Deduplication strictly improves validation hygiene."]
        else:
            cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
            transform_class = TransformationClass.TYPE_UNIFICATION.value
            uniformity = obs.evidence.get("type_uniformity_score", 0.50)
            mechanism = f"Inconsistent data type parsing (Type uniformity = {uniformity:.1%})."
            summary = (
                f"Column {cols} contains mixed data types (type uniformity = {uniformity:.1%}). "
                f"Mixed types cause execution crashes in numerical linear algebra routines. "
                f"Casting column {cols} to a unified dtype resolves schema inconsistency."
            )
            assumptions = ["Column values can be coercion-parsed to a single dominant data type."]
            risks = ["Values failing type conversion will be coerced to NaN."]

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.95,
            assumptions=assumptions,
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=risks
        )


class FeatureQualityReasoningTemplate(BaseReasoningTemplate):
    """Reasoning template for Feature Quality flaws (constant & ID columns)."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        cols = ", ".join([f"'{c}'" for c in obs.affected_columns])

        transform_class = TransformationClass.FEATURE_DROP.value

        if "constant" in obs.title.lower() or "constant_columns" in obs.evidence:
            mechanism = "Zero-variance constant feature non-informativeness."
            summary = (
                f"Column(s) {cols} carry zero statistical variance across all rows. "
                f"Constant features carry 0 predictive information and waste memory/computation. "
                f"Dropping constant feature(s) {cols} simplifies model hypothesis space."
            )
            assumptions = ["Constant features carry 0 information for downstream modeling."]
            risks = ["None. Dropping zero-variance features is mathematically safe."]
        else:
            mechanism = "High-cardinality unique string identifier leakage."
            summary = (
                f"Column(s) {cols} contain 100% unique string values matching ID patterns. "
                f"High-cardinality ID strings induce severe target memorization and model overfitting. "
                f"Excluding identifier feature(s) {cols} prevents spurious correlation."
            )
            assumptions = ["Unique string IDs carry no generalizable pattern."]
            risks = ["Loss of identifier tracking if needed for post-inference indexing."]

        return ReasoningTemplateResult(
            reasoning_summary=summary,
            inferred_mechanism=mechanism,
            recommended_transformation_class=transform_class,
            confidence=0.98,
            assumptions=assumptions,
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=risks
        )


class FallbackReasoningTemplate(BaseReasoningTemplate):
    """Fallback reasoning template for custom or unrecognized observation categories."""

    def reason(self, problem: RankedProblem) -> ReasoningTemplateResult:
        obs = problem.observation
        cols = ", ".join([f"'{c}'" for c in obs.affected_columns]) or "dataset"
        return ReasoningTemplateResult(
            reasoning_summary=f"Custom statistical flaw detected in {cols}: '{obs.title}'.",
            inferred_mechanism="Empirical anomaly detected during dataset profiling.",
            recommended_transformation_class=TransformationClass.FEATURE_DROP.value,
            confidence=0.75,
            assumptions=["The observed anomaly negatively affects dataset health."],
            constraints=list(DEFAULT_SYSTEM_CONSTRAINTS),
            risks=["Uncertain transformation impact due to non-standard flaw category."]
        )


# Template Registry Factory
TEMPLATE_REGISTRY: Dict[ObservationCategory, BaseReasoningTemplate] = {
    ObservationCategory.COMPLETENESS: CompletenessReasoningTemplate(),
    ObservationCategory.CORRELATION: CorrelationReasoningTemplate(),
    ObservationCategory.BALANCE: BalanceReasoningTemplate(),
    ObservationCategory.NOISE: NoiseReasoningTemplate(),
    ObservationCategory.CONSISTENCY: ConsistencyReasoningTemplate(),
    ObservationCategory.FEATURE_QUALITY: FeatureQualityReasoningTemplate(),
}

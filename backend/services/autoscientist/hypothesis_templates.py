"""
services/autoscientist/hypothesis_templates.py — Template Generators for Scientific Hypotheses.

Synthesizes testable, measurable, and falsifiable scientific claim statements,
proposed parameters via ParameterFactory, predicted metric deltas, and risk assessments.
"""

from typing import Any, Dict, List, Optional
from services.autoscientist.hypothesis_constants import ParameterFactory, RiskLevel
from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.reasoning_models import ReasoningTrace


class HypothesisTemplateResult:
    """Structured container holding template output fields for ScientificHypothesis assembly."""
    def __init__(
        self,
        statement: str,
        target_column: Optional[str],
        proposed_parameters: Dict[str, Any],
        target_evaluation_metric: str,
        predicted_metric_delta: float,
        estimated_confidence: float,
        risk_level: RiskLevel,
        expected_side_effects: List[str]
    ):
        self.statement = statement
        self.target_column = target_column
        self.proposed_parameters = proposed_parameters
        self.target_evaluation_metric = target_evaluation_metric
        self.predicted_metric_delta = predicted_metric_delta
        self.estimated_confidence = estimated_confidence
        self.risk_level = risk_level
        self.expected_side_effects = expected_side_effects


class BaseHypothesisTemplate:
    """Base interface for category-specific hypothesis templates."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        raise NotImplementedError


class CompletenessHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Completeness flaws."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence
        missing_rate = evidence.get("missing_rate") or evidence.get("missing_cell_ratio", 0.10)
        col_name = evidence.get("column_name")

        if trace.recommended_transformation_class == "FeatureDropTransformation":
            target_cols = [col_name] if col_name else evidence.get("constant_columns", ["missing_col"])
            params = ParameterFactory.feature_drop(drop_columns=target_cols)
            statement = (
                f"Applying FeatureDropTransformation to drop column '{target_cols[0]}' "
                f"(missing rate = {missing_rate:.1%}) will eliminate uninformative missingness noise, "
                f"improving baseline downstream classifier f1_score by at least +0.035."
            )
            delta = min(0.120, max(0.020, missing_rate * 0.15))
            risk = RiskLevel.HIGH if missing_rate > 0.70 else RiskLevel.MEDIUM
            side_effects = ["Permanent loss of feature column for model inference."]
            target_col = target_cols[0]
        else:
            target_col = col_name or "imputed_col"
            params = ParameterFactory.knn_imputation(n_neighbors=5, weights="uniform")
            statement = (
                f"Applying ImputationTransformation (KNN n_neighbors=5) to impute missing values in '{target_col}' "
                f"(missing rate = {missing_rate:.1%}) will restore dataset completeness, "
                f"improving downstream classifier f1_score by at least +0.045."
            )
            delta = min(0.100, max(0.015, missing_rate * 0.20))
            risk = RiskLevel.MEDIUM
            side_effects = ["Synthetic value variance smoothing in imputed rows."]

        conf = max(0.70, min(0.95, trace.confidence * 0.95))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=target_col,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=risk,
            expected_side_effects=side_effects
        )


class CorrelationHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Correlation flaws (multicollinearity)."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence
        col_1 = evidence.get("column_1", "col_a")
        col_2 = evidence.get("column_2", "col_b")
        abs_r = evidence.get("absolute_coefficient", 0.90)

        params = ParameterFactory.feature_pruning(retain_column=col_1, prune_column=col_2)
        statement = (
            f"Applying FeaturePruningTransformation to prune redundant feature '{col_2}' "
            f"(correlated with '{col_1}', |r| = {abs_r:.2f}) will eliminate matrix ill-conditioning, "
            f"improving downstream classifier f1_score by at least +0.025."
        )
        delta = min(0.080, max(0.010, (abs_r - 0.85) * 0.25 + 0.015))
        conf = max(0.75, min(0.96, trace.confidence * 0.98))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=col_2,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=RiskLevel.LOW,
            expected_side_effects=["Slight reduction in overall feature space dimensionality."]
        )


class BalanceHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Balance flaws (class imbalance)."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence
        col_name = evidence.get("column_name", "target_col")
        maj_ratio = evidence.get("majority_class_ratio", 0.85)

        params = ParameterFactory.smote(sampling_strategy="auto", k_neighbors=5)
        statement = (
            f"Applying ClassRebalancingTransformation (SMOTE sampling_strategy='auto') to rebalance target feature '{col_name}' "
            f"(majority class ratio = {maj_ratio:.1%}) will prevent decision boundary collapse, "
            f"improving downstream minority class f1_score by at least +0.060."
        )
        delta = min(0.180, max(0.030, (maj_ratio - 0.85) * 0.40 + 0.030))
        conf = max(0.70, min(0.92, trace.confidence * 0.92))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=col_name,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=RiskLevel.HIGH,
            expected_side_effects=["Increased training dataset row count via synthetic observation generation."]
        )


class NoiseHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Noise flaws (IQR outliers)."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence
        col_name = evidence.get("column_name", "numeric_col")
        outlier_ratio = evidence.get("outlier_ratio", 0.05)

        params = ParameterFactory.winsorization(lower_quantile=0.01, upper_quantile=0.99)
        statement = (
            f"Applying WinsorizationTransformation (quantile bounds [0.01, 0.99]) on feature '{col_name}' "
            f"(outlier ratio = {outlier_ratio:.1%}) will restrict gradient destabilization from extreme noise, "
            f"improving downstream classifier f1_score by at least +0.030."
        )
        delta = min(0.090, max(0.010, outlier_ratio * 0.30))
        conf = max(0.75, min(0.95, trace.confidence * 0.95))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=col_name,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=RiskLevel.MEDIUM,
            expected_side_effects=["Truncation of extreme values to the 1st and 99th percentiles."]
        )


class ConsistencyHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Consistency flaws (duplicates & mixed types)."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence

        if trace.recommended_transformation_class == "RowDeduplicationTransformation":
            dup_rows = evidence.get("duplicate_rows", 0)
            dup_ratio = evidence.get("duplicate_ratio", 0.01)
            params = ParameterFactory.row_deduplication(keep="first")
            statement = (
                f"Applying RowDeduplicationTransformation to remove {dup_rows:,} exact duplicate rows "
                f"({dup_ratio:.1%}) will eliminate train-test data leakage, "
                f"improving downstream validation integrity and f1_score by at least +0.020."
            )
            delta = min(0.050, max(0.005, dup_ratio * 0.50 + 0.005))
            target_col = None
            risk = RiskLevel.LOW
            side_effects = ["Reduction in total row count by deduplicated count."]
        else:
            col_name = evidence.get("column_name", "mixed_col")
            params = ParameterFactory.type_unification(target_type="numeric_coerced")
            statement = (
                f"Applying TypeUnificationTransformation to coerce column '{col_name}' to a unified numeric data type "
                f"will eliminate parsing crashes and restore feature matrix alignment, "
                f"improving downstream classifier f1_score by at least +0.040."
            )
            delta = 0.040
            target_col = col_name
            risk = RiskLevel.MEDIUM
            side_effects = ["Non-convertible string entries will be coerced to NaN."]

        conf = max(0.80, min(0.98, trace.confidence * 0.98))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=target_col,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=risk,
            expected_side_effects=side_effects
        )


class FeatureQualityHypothesisTemplate(BaseHypothesisTemplate):
    """Hypothesis template for Feature Quality flaws (constant & ID columns)."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        evidence = trace.supporting_evidence

        if "constant_columns" in evidence:
            constant_cols = evidence.get("constant_columns", ["constant_col"])
            params = ParameterFactory.feature_drop(drop_columns=constant_cols)
            cols_str = ", ".join([f"'{c}'" for c in constant_cols])
            statement = (
                f"Applying FeatureDropTransformation to drop zero-variance constant column(s) {cols_str} "
                f"will eliminate non-informative feature dimensions, "
                f"improving model training efficiency and f1_score by at least +0.020."
            )
            target_col = constant_cols[0]
            delta = 0.020
            risk = RiskLevel.LOW
            side_effects = ["Zero variance columns excluded from feature set."]
        else:
            id_cols = evidence.get("id_like_columns", ["id_col"])
            params = ParameterFactory.feature_drop(drop_columns=id_cols)
            cols_str = ", ".join([f"'{c}'" for c in id_cols])
            statement = (
                f"Applying FeatureDropTransformation to exclude high-cardinality string identifier column(s) {cols_str} "
                f"will prevent target memorization and model overfitting, "
                f"improving test set generalization f1_score by at least +0.050."
            )
            target_col = id_cols[0]
            delta = 0.050
            risk = RiskLevel.LOW
            side_effects = ["Identifier column excluded from feature matrix."]

        conf = max(0.85, min(0.99, trace.confidence * 0.99))

        return HypothesisTemplateResult(
            statement=statement,
            target_column=target_col,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=round(delta, 4),
            estimated_confidence=round(conf, 4),
            risk_level=risk,
            expected_side_effects=side_effects
        )


class FallbackHypothesisTemplate(BaseHypothesisTemplate):
    """Fallback hypothesis template for custom or non-standard categories."""

    def generate(self, trace: ReasoningTrace) -> HypothesisTemplateResult:
        target_col = trace.supporting_evidence.get("column_name")
        params = ParameterFactory.feature_drop(drop_columns=[target_col] if target_col else ["flawed_col"])
        statement = (
            f"Applying {trace.recommended_transformation_class} to remediate issue '{trace.problem_id}' "
            f"will improve baseline downstream classifier f1_score by at least +0.010."
        )
        return HypothesisTemplateResult(
            statement=statement,
            target_column=target_col,
            proposed_parameters=params,
            target_evaluation_metric="f1_score",
            predicted_metric_delta=0.010,
            estimated_confidence=0.75,
            risk_level=RiskLevel.MEDIUM,
            expected_side_effects=["Dataset modification according to fallback strategy."]
        )


# Category Template Registry
HYPOTHESIS_TEMPLATE_REGISTRY: Dict[ObservationCategory, BaseHypothesisTemplate] = {
    ObservationCategory.COMPLETENESS: CompletenessHypothesisTemplate(),
    ObservationCategory.CORRELATION: CorrelationHypothesisTemplate(),
    ObservationCategory.BALANCE: BalanceHypothesisTemplate(),
    ObservationCategory.NOISE: NoiseHypothesisTemplate(),
    ObservationCategory.CONSISTENCY: ConsistencyHypothesisTemplate(),
    ObservationCategory.FEATURE_QUALITY: FeatureQualityHypothesisTemplate(),
}

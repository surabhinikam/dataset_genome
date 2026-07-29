"""
services/autoscientist/ranking_explainer.py — Natural Language Explanation Generator.

Synthesizes rich, human-readable justifications explaining utility scores, ranking priority,
and actionable next steps for downstream hypothesis generation.
"""

from services.autoscientist.observation_constants import ObservationCategory
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_models import UtilityComponents


class RankingExplainer:
    """
    Generates human-readable explanations and actionable recommended next steps
    for prioritized problems in the AutoScientist pipeline.
    """

    @staticmethod
    def generate_explanation(
        obs: ScientificObservation,
        utility_score: float,
        components: UtilityComponents
    ) -> str:
        """Synthesize narrative explanation for why this problem received its utility score."""
        category_name = obs.category.value.replace("_", " ").title()
        
        explanation = (
            f"Assigned utility score of {utility_score:.4f} (Rank Component Breakdown: "
            f"Severity={components.severity:.2f}, Info Loss Risk={components.information_loss_risk:.2f}, "
            f"Impact Potential={components.impact_potential:.2f}, Complexity Penalty={components.repair_complexity:.2f}). "
            f"This {category_name} issue '{obs.title}' affects {len(obs.affected_columns)} column(s) "
            f"with statistical confidence of {obs.confidence:.0%}."
        )
        return explanation

    @staticmethod
    def generate_recommended_next_step(obs: ScientificObservation) -> str:
        """Formulate specific recommendation for downstream Hypothesis Generator & Experiment Planner."""
        if obs.category == ObservationCategory.FEATURE_QUALITY:
            if "constant_columns" in obs.evidence:
                cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
                return f"Formulate mutation hypothesis to drop zero-variance constant feature(s): {cols}."
            if "id_like_columns" in obs.evidence:
                cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
                return f"Formulate mutation hypothesis to exclude high-cardinality string identifier column(s): {cols}."

        elif obs.category == ObservationCategory.COMPLETENESS:
            cols = ", ".join([f"'{c}'" for c in obs.affected_columns[:3]])
            if len(obs.affected_columns) > 3:
                cols += f" and {len(obs.affected_columns) - 3} other(s)"
            return f"Formulate hypothesis for KNN / median-mode missing value imputation targeting column(s): {cols}."

        elif obs.category == ObservationCategory.CORRELATION:
            cols = " & ".join([f"'{c}'" for c in obs.affected_columns])
            return f"Formulate hypothesis to prune redundant feature from collinear pair: {cols}."

        elif obs.category == ObservationCategory.NOISE:
            cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
            return f"Formulate hypothesis for Winsorization or quantile clipping on noisy feature(s): {cols}."

        elif obs.category == ObservationCategory.BALANCE:
            cols = ", ".join([f"'{c}'" for c in obs.affected_columns])
            return f"Formulate hypothesis for SMOTE or random oversampling on imbalanced target feature(s): {cols}."

        elif obs.category == ObservationCategory.CONSISTENCY:
            if "duplicate" in obs.title.lower():
                return "Formulate mutation hypothesis to remove exact duplicate rows."
            return f"Formulate hypothesis to cast mixed-type feature(s) to a unified data type."

        # Fallback recommendation
        if obs.recommendations:
            return obs.recommendations[0]
        return f"Formulate corrective dataset mutation hypothesis targeting issue '{obs.title}'."

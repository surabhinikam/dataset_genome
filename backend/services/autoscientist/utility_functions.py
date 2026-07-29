"""
services/autoscientist/utility_functions.py — Multi-Criteria Utility Calculation Engine.

Calculates normalized component scores (severity, information loss risk, impact potential,
and repair complexity) and computes the final scalar utility score according to AUTOSCIENTIST_SPEC.md.
"""

from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.ranking_constants import (
    CATEGORY_IMPACT_POTENTIAL,
    CATEGORY_INFO_LOSS_RISK,
    CATEGORY_REPAIR_COMPLEXITY,
    WEIGHT_IMPACT_POTENTIAL,
    WEIGHT_INFO_LOSS_RISK,
    WEIGHT_REPAIR_COMPLEXITY_PENALTY,
    WEIGHT_SEVERITY,
    ObservationCategory,
)
from services.autoscientist.ranking_models import UtilityComponents


class UtilityCalculator:
    """
    Computes multi-criteria utility scores for scientific dataset observations.
    
    Formula:
      U(O_i) = w1 * Severity + w2 * InfoLossRisk + w3 * ImpactPotential - w4 * RepairComplexity
    
    All input metrics are strictly normalized in [0.0, 1.0].
    The final utility score is clamped to [0.0, 1.0].
    """

    @staticmethod
    def _clamp(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        return max(min_val, min(max_val, val))

    @classmethod
    def calculate_info_loss_risk(cls, obs: ScientificObservation) -> float:
        """Calculate Information Loss Risk component normalized to [0.0, 1.0]."""
        base_risk = CATEGORY_INFO_LOSS_RISK.get(obs.category, 0.50)

        # Refine based on specific evidence payload values
        if obs.category == ObservationCategory.COMPLETENESS:
            missing_rate = obs.evidence.get("missing_cell_ratio") or obs.evidence.get("missing_rate", 0.0)
            if missing_rate > 0.50:
                base_risk = 0.95
        elif obs.category == ObservationCategory.FEATURE_QUALITY:
            if "constant_columns" in obs.evidence:
                base_risk = 1.0  # Constant features carry maximum structural waste

        return round(cls._clamp(base_risk), 4)

    @classmethod
    def calculate_impact_potential(cls, obs: ScientificObservation) -> float:
        """Calculate Impact Potential component normalized to [0.0, 1.0]."""
        base_impact = CATEGORY_IMPACT_POTENTIAL.get(obs.category, 0.60)

        # Scale by severity multiplier
        impact = base_impact * (0.50 + 0.50 * obs.severity)
        return round(cls._clamp(impact), 4)

    @classmethod
    def calculate_repair_complexity(cls, obs: ScientificObservation) -> float:
        """Calculate Repair Complexity penalty component normalized to [0.0, 1.0]."""
        base_complexity = CATEGORY_REPAIR_COMPLEXITY.get(obs.category, 0.50)

        # Refine based on specific remediation details
        if obs.category == ObservationCategory.COMPLETENESS:
            # Imputing many columns is more complex than a single column drop
            if len(obs.affected_columns) > 3:
                base_complexity = 0.65
        elif obs.category == ObservationCategory.NOISE:
            if obs.evidence.get("outlier_ratio", 0.0) > 0.10:
                base_complexity = 0.60

        return round(cls._clamp(base_complexity), 4)

    @classmethod
    def compute_components(cls, obs: ScientificObservation) -> UtilityComponents:
        """Compute all 4 normalized utility component scores."""
        sev = cls._clamp(obs.severity)
        info_risk = cls.calculate_info_loss_risk(obs)
        impact = cls.calculate_impact_potential(obs)
        complexity = cls.calculate_repair_complexity(obs)

        return UtilityComponents(
            severity=round(sev, 4),
            information_loss_risk=round(info_risk, 4),
            impact_potential=round(impact, 4),
            repair_complexity=round(complexity, 4),
        )

    @classmethod
    def compute_utility_score(cls, obs: ScientificObservation, components: UtilityComponents) -> float:
        """
        Compute scalar utility score U(O_i) using weighted linear combination.
        """
        raw_utility = (
            WEIGHT_SEVERITY * components.severity
            + WEIGHT_INFO_LOSS_RISK * components.information_loss_risk
            + WEIGHT_IMPACT_POTENTIAL * components.impact_potential
            - WEIGHT_REPAIR_COMPLEXITY_PENALTY * components.repair_complexity
        )
        return round(cls._clamp(raw_utility), 4)

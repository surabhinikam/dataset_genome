"""
services/autoscientist/severity_engine.py — Normalized Severity Calculation Engine.

Calculates normalized severity scores strictly bounded between 0.0 (minimal/no issue)
and 1.0 (critical flaw) based on empirical statistical deviations from reference thresholds.
"""

import math
from typing import Dict, Any

from services.autoscientist.observation_constants import (
    CATEGORY_SEVERITY_WEIGHTS,
    CRITICAL_COLUMN_MISSING_THRESHOLD,
    DUPLICATE_ROW_RATIO_THRESHOLD,
    MAJORITY_CLASS_RATIO_THRESHOLD,
    MISSING_CELL_RATIO_THRESHOLD,
    MISSING_COLUMN_RATIO_THRESHOLD,
    OUTLIER_RATIO_THRESHOLD,
    PEARSON_CORRELATION_THRESHOLD,
    SEVERE_OUTLIER_RATIO_THRESHOLD,
    TYPE_UNIFORMITY_THRESHOLD,
    ObservationCategory,
)


class SeverityEngine:
    """
    Normalized Severity Calculation Engine for Dataset Genome observations.
    
    Computes calibrated severity metrics in the closed interval [0.0, 1.0]
    using continuous mathematical scaling functions.
    """

    @staticmethod
    def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Helper to clamp float values within [min_val, max_val]."""
        return max(min_val, min(max_val, value))

    @classmethod
    def calculate_completeness_cell_severity(cls, missing_cell_ratio: float) -> float:
        """
        Calculate severity for overall missing cell ratio.
        
        Ratio < 5%: Severity = 0.0
        Ratio >= 5%: Linear scaling up to 50% missingness = 1.0
        """
        if missing_cell_ratio < MISSING_CELL_RATIO_THRESHOLD:
            return 0.0
        raw_sev = (missing_cell_ratio - MISSING_CELL_RATIO_THRESHOLD) / (0.50 - MISSING_CELL_RATIO_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_column_missing_severity(cls, col_missing_rate: float) -> float:
        """
        Calculate severity for a specific column missing rate.
        
        Rate < 10%: Severity = 0.0
        Rate >= 10%: Scaled non-linearly to 1.0 at 80%+ missingness.
        """
        if col_missing_rate < MISSING_COLUMN_RATIO_THRESHOLD:
            return 0.0
        raw_sev = (col_missing_rate - MISSING_COLUMN_RATIO_THRESHOLD) / (0.80 - MISSING_COLUMN_RATIO_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_duplicate_rows_severity(cls, duplicate_ratio: float) -> float:
        """
        Calculate severity for duplicate row ratio.
        
        Ratio < 1%: Severity = 0.0
        Ratio >= 1%: Scaled linearly to 1.0 at 20%+ duplicates.
        """
        if duplicate_ratio < DUPLICATE_ROW_RATIO_THRESHOLD:
            return 0.0
        raw_sev = (duplicate_ratio - DUPLICATE_ROW_RATIO_THRESHOLD) / (0.20 - DUPLICATE_ROW_RATIO_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_type_uniformity_severity(cls, uniformity_score: float) -> float:
        """
        Calculate severity for mixed data types in a column.
        
        Uniformity >= 95%: Severity = 0.0
        Uniformity < 95%: Scaled to 1.0 at 50% mixed types.
        """
        if uniformity_score >= TYPE_UNIFORMITY_THRESHOLD:
            return 0.0
        raw_sev = (TYPE_UNIFORMITY_THRESHOLD - uniformity_score) / (TYPE_UNIFORMITY_THRESHOLD - 0.50)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_class_imbalance_severity(cls, majority_class_ratio: float) -> float:
        """
        Calculate severity for categorical class imbalance.
        
        Majority Ratio < 85%: Severity = 0.0
        Majority Ratio >= 85%: Scaled to 1.0 at 99%+ majority class.
        """
        if majority_class_ratio < MAJORITY_CLASS_RATIO_THRESHOLD:
            return 0.0
        raw_sev = (majority_class_ratio - MAJORITY_CLASS_RATIO_THRESHOLD) / (0.99 - MAJORITY_CLASS_RATIO_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_correlation_severity(cls, pearson_coeff: float) -> float:
        """
        Calculate severity for pairwise feature multicollinearity.
        
        |r| < 0.85: Severity = 0.0
        |r| >= 0.85: Scaled linearly to 1.0 at |r| = 1.0
        """
        abs_r = abs(pearson_coeff)
        if abs_r < PEARSON_CORRELATION_THRESHOLD:
            return 0.0
        raw_sev = (abs_r - PEARSON_CORRELATION_THRESHOLD) / (1.0 - PEARSON_CORRELATION_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_outlier_severity(cls, outlier_ratio: float) -> float:
        """
        Calculate severity for IQR column outliers.
        
        Ratio < 3%: Severity = 0.0
        Ratio >= 3%: Scaled linearly to 1.0 at 15%+ outliers.
        """
        if outlier_ratio < OUTLIER_RATIO_THRESHOLD:
            return 0.0
        raw_sev = (outlier_ratio - OUTLIER_RATIO_THRESHOLD) / (0.15 - OUTLIER_RATIO_THRESHOLD)
        return round(cls._clamp(raw_sev), 4)

    @classmethod
    def calculate_constant_column_severity(cls) -> float:
        """Zero-variance constant columns carry maximum severity (1.0)."""
        return 1.0

    @classmethod
    def calculate_low_variance_severity(cls) -> float:
        """Near-zero low variance columns carry medium severity (0.50)."""
        return 0.50

    @classmethod
    def calculate_id_like_column_severity(cls) -> float:
        """100% unique string ID columns carry medium-high severity (0.70)."""
        return 0.70

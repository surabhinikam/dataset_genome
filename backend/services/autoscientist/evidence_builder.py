"""
services/autoscientist/evidence_builder.py — Empirical Evidence Payload Builder.

Synthesizes structured, JSON-serializable evidence payloads containing raw
metrics, mathematical quantiles, thresholds, and counts for every observation.
"""

from typing import Any, Dict, List, Optional
from schemas.intelligence import ColumnOutlierDetail, CorrelationPair


class EvidenceBuilder:
    """
    Constructs rich, self-contained empirical evidence payloads
    documenting statistical grounds for scientific observations.
    """

    @staticmethod
    def build_completeness_evidence(
        total_cells: int,
        missing_cells: int,
        missing_cell_ratio: float,
        complete_row_ratio: float,
        threshold: float,
        affected_column_count: int
    ) -> Dict[str, Any]:
        """Build evidence payload for general missing value completeness."""
        return {
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "missing_cell_ratio": round(missing_cell_ratio, 4),
            "complete_row_ratio": round(complete_row_ratio, 4),
            "reference_threshold": threshold,
            "affected_column_count": affected_column_count,
        }

    @staticmethod
    def build_column_missing_evidence(
        column_name: str,
        missing_rate: float,
        total_rows: int,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for a specific column missing rate."""
        missing_row_count = int(round(missing_rate * total_rows))
        return {
            "column_name": column_name,
            "missing_rate": round(missing_rate, 4),
            "missing_row_count": missing_row_count,
            "total_rows": total_rows,
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_duplicate_rows_evidence(
        total_rows: int,
        duplicate_rows: int,
        duplicate_ratio: float,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for duplicate rows."""
        return {
            "total_rows": total_rows,
            "duplicate_rows": duplicate_rows,
            "duplicate_ratio": round(duplicate_ratio, 4),
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_mixed_types_evidence(
        column_name: str,
        uniformity_score: float,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for mixed column data types."""
        return {
            "column_name": column_name,
            "type_uniformity_score": round(uniformity_score, 4),
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_class_imbalance_evidence(
        column_name: str,
        majority_class_ratio: float,
        entropy: float,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for categorical class imbalance."""
        return {
            "column_name": column_name,
            "majority_class_ratio": round(majority_class_ratio, 4),
            "shannon_entropy": round(entropy, 4),
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_correlation_pair_evidence(
        pair: CorrelationPair,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for pairwise feature multicollinearity."""
        return {
            "column_1": pair.column_1,
            "column_2": pair.column_2,
            "pearson_coefficient": round(pair.coefficient, 4),
            "absolute_coefficient": round(abs(pair.coefficient), 4),
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_outlier_column_evidence(
        column_name: str,
        detail: ColumnOutlierDetail,
        threshold: float
    ) -> Dict[str, Any]:
        """Build evidence payload for IQR column outliers."""
        return {
            "column_name": column_name,
            "outlier_count": detail.outlier_count,
            "outlier_ratio": round(detail.outlier_ratio, 4),
            "q1": round(detail.q1, 4),
            "q3": round(detail.q3, 4),
            "iqr": round(detail.iqr, 4),
            "lower_bound": round(detail.lower_bound, 4),
            "upper_bound": round(detail.upper_bound, 4),
            "reference_threshold": threshold,
        }

    @staticmethod
    def build_constant_column_evidence(
        constant_columns: List[str]
    ) -> Dict[str, Any]:
        """Build evidence payload for zero-variance constant features."""
        return {
            "constant_columns": constant_columns,
            "count": len(constant_columns),
            "variance": 0.0,
        }

    @staticmethod
    def build_id_like_column_evidence(
        id_columns: List[str]
    ) -> Dict[str, Any]:
        """Build evidence payload for 100% unique string ID columns."""
        return {
            "id_like_columns": id_columns,
            "count": len(id_columns),
            "uniqueness_ratio": 1.0,
        }

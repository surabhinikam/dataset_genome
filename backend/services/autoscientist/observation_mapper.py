"""
services/autoscientist/observation_mapper.py — Observation Mapper for Sprint 2 Profiler Results.

Maps every section of a GenomeReportResponse (Completeness, Consistency, Balance,
Correlation, Noise, Feature Quality) into calibrated ScientificObservation domain models.
"""

import re
from typing import List

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evidence_builder import EvidenceBuilder
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import (
    DEFAULT_CONFIDENCE,
    DUPLICATE_ROW_RATIO_THRESHOLD,
    HEURISTIC_CONFIDENCE,
    MAJORITY_CLASS_RATIO_THRESHOLD,
    MISSING_CELL_RATIO_THRESHOLD,
    MISSING_COLUMN_RATIO_THRESHOLD,
    OUTLIER_RATIO_THRESHOLD,
    PEARSON_CORRELATION_THRESHOLD,
    TYPE_UNIFORMITY_THRESHOLD,
    ObservationCategory,
)
from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.severity_engine import SeverityEngine


def _slugify(text: str) -> str:
    """Pure-Python slugify helper converting arbitrary string to URL/ID safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-') or "col"


class ObservationMapper:
    """
    Translates raw quantitative profiling results from a GenomeReportResponse
    into canonical, structured ScientificObservation domain models.
    """

    @classmethod
    def map_completeness(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Completeness Profiler."""
        observations: List[ScientificObservation] = []
        comp = report.completeness

        # 1. Overall Cell Missingness Observation
        if comp.missing_cell_ratio >= MISSING_CELL_RATIO_THRESHOLD:
            severity = SeverityEngine.calculate_completeness_cell_severity(comp.missing_cell_ratio)
            evidence = EvidenceBuilder.build_completeness_evidence(
                total_cells=comp.total_cells,
                missing_cells=comp.missing_cells,
                missing_cell_ratio=comp.missing_cell_ratio,
                complete_row_ratio=comp.complete_row_ratio,
                threshold=MISSING_CELL_RATIO_THRESHOLD,
                affected_column_count=len(comp.column_missing_rates)
            )
            affected_cols = [col for col, rate in comp.column_missing_rates.items() if rate > 0]

            obs = (
                ScientificObservationBuilder()
                .with_id(f"obs-comp-overall-{report.dataset_id}")
                .with_category(ObservationCategory.COMPLETENESS)
                .with_title(f"Dataset-Wide Missing Cell Ratio ({comp.missing_cell_ratio:.1%})")
                .with_summary(
                    f"Dataset contains {comp.missing_cells:,} missing cells across "
                    f"{len(affected_cols)} columns, yielding an overall missing cell ratio of {comp.missing_cell_ratio:.1%}."
                )
                .with_affected_columns(affected_cols)
                .with_severity(severity)
                .with_confidence(DEFAULT_CONFIDENCE)
                .with_evidence(evidence)
                .with_recommendations([
                    "Evaluate column-level missingness before model training.",
                    "Apply missing value imputation (KNN / MICE / Median mode fallback) or drop severely missing columns."
                ])
                .build()
            )
            observations.append(obs)

        # 2. Per-Column Severe Missingness Observations
        for col_name, rate in comp.column_missing_rates.items():
            if rate >= MISSING_COLUMN_RATIO_THRESHOLD:
                severity = SeverityEngine.calculate_column_missing_severity(rate)
                evidence = EvidenceBuilder.build_column_missing_evidence(
                    column_name=col_name,
                    missing_rate=rate,
                    total_rows=report.num_rows,
                    threshold=MISSING_COLUMN_RATIO_THRESHOLD
                )
                slug_col = _slugify(col_name)

                obs = (
                    ScientificObservationBuilder()
                    .with_id(f"obs-comp-col-{slug_col}-{report.dataset_id}")
                    .with_category(ObservationCategory.COMPLETENESS)
                    .with_title(f"High Missing Rate in Column '{col_name}' ({rate:.1%})")
                    .with_summary(
                        f"Column '{col_name}' is missing {rate:.1%} of its values "
                        f"({int(round(rate * report.num_rows)):,}/{report.num_rows:,} rows)."
                    )
                    .with_affected_columns([col_name])
                    .with_severity(severity)
                    .with_confidence(DEFAULT_CONFIDENCE)
                    .with_evidence(evidence)
                    .with_recommendations([
                        f"If missing rate > 50%, consider dropping feature '{col_name}'.",
                        f"Otherwise apply model-based imputation (e.g. KNNImputer) for '{col_name}'."
                    ])
                    .build()
                )
                observations.append(obs)

        return observations

    @classmethod
    def map_consistency(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Consistency Profiler."""
        observations: List[ScientificObservation] = []
        cons = report.consistency

        # 1. Duplicate Rows Observation
        if cons.duplicate_ratio >= DUPLICATE_ROW_RATIO_THRESHOLD:
            severity = SeverityEngine.calculate_duplicate_rows_severity(cons.duplicate_ratio)
            evidence = EvidenceBuilder.build_duplicate_rows_evidence(
                total_rows=cons.total_rows,
                duplicate_rows=cons.duplicate_rows,
                duplicate_ratio=cons.duplicate_ratio,
                threshold=DUPLICATE_ROW_RATIO_THRESHOLD
            )

            obs = (
                ScientificObservationBuilder()
                .with_id(f"obs-cons-dups-{report.dataset_id}")
                .with_category(ObservationCategory.CONSISTENCY)
                .with_title(f"Duplicate Rows Detected ({cons.duplicate_rows:,} rows, {cons.duplicate_ratio:.1%})")
                .with_summary(
                    f"Dataset contains {cons.duplicate_rows:,} exact duplicate rows "
                    f"({cons.duplicate_ratio:.1%} of {cons.total_rows:,} total rows)."
                )
                .with_severity(severity)
                .with_confidence(DEFAULT_CONFIDENCE)
                .with_evidence(evidence)
                .with_recommendations([
                    "Deduplicate exact duplicate rows to prevent train-test data leakage."
                ])
                .build()
            )
            observations.append(obs)

        # 2. Mixed Type Columns Observation
        for col_name in cons.mixed_type_columns:
            uniformity = cons.type_uniformity_scores.get(col_name, 0.50)
            if uniformity < TYPE_UNIFORMITY_THRESHOLD:
                severity = SeverityEngine.calculate_type_uniformity_severity(uniformity)
                evidence = EvidenceBuilder.build_mixed_types_evidence(
                    column_name=col_name,
                    uniformity_score=uniformity,
                    threshold=TYPE_UNIFORMITY_THRESHOLD
                )
                slug_col = _slugify(col_name)

                obs = (
                    ScientificObservationBuilder()
                    .with_id(f"obs-cons-mixed-{slug_col}-{report.dataset_id}")
                    .with_category(ObservationCategory.CONSISTENCY)
                    .with_title(f"Mixed Data Types in Column '{col_name}' (Uniformity: {uniformity:.1%})")
                    .with_summary(
                        f"Column '{col_name}' contains inconsistent mixed Python types with "
                        f"a type uniformity score of {uniformity:.1%}."
                    )
                    .with_affected_columns([col_name])
                    .with_severity(severity)
                    .with_confidence(DEFAULT_CONFIDENCE)
                    .with_evidence(evidence)
                    .with_recommendations([
                        f"Cast column '{col_name}' to a unified data type (numeric, categorical, or string)."
                    ])
                    .build()
                )
                observations.append(obs)

        return observations

    @classmethod
    def map_balance(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Balance Profiler."""
        observations: List[ScientificObservation] = []
        bal = report.balance

        for col_name in bal.imbalanced_columns:
            maj_ratio = bal.majority_class_ratios.get(col_name, 0.85)
            entropy = bal.categorical_entropy.get(col_name, 0.0)

            if maj_ratio >= MAJORITY_CLASS_RATIO_THRESHOLD:
                severity = SeverityEngine.calculate_class_imbalance_severity(maj_ratio)
                evidence = EvidenceBuilder.build_class_imbalance_evidence(
                    column_name=col_name,
                    majority_class_ratio=maj_ratio,
                    entropy=entropy,
                    threshold=MAJORITY_CLASS_RATIO_THRESHOLD
                )
                slug_col = _slugify(col_name)

                obs = (
                    ScientificObservationBuilder()
                    .with_id(f"obs-bal-{slug_col}-{report.dataset_id}")
                    .with_category(ObservationCategory.BALANCE)
                    .with_title(f"Severe Class Imbalance in Column '{col_name}' ({maj_ratio:.1%})")
                    .with_summary(
                        f"Column '{col_name}' exhibits severe class imbalance. The majority class "
                        f"accounts for {maj_ratio:.1%} of observations (Shannon Entropy: {entropy:.2f})."
                    )
                    .with_affected_columns([col_name])
                    .with_severity(severity)
                    .with_confidence(DEFAULT_CONFIDENCE)
                    .with_evidence(evidence)
                    .with_recommendations([
                        f"Consider class rebalancing techniques (SMOTE, Random Oversampling/Undersampling) for '{col_name}'."
                    ])
                    .build()
                )
                observations.append(obs)

        return observations

    @classmethod
    def map_correlation(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Correlation Profiler."""
        observations: List[ScientificObservation] = []
        corr = report.correlation

        for pair in corr.high_correlation_pairs:
            abs_r = abs(pair.coefficient)
            if abs_r >= PEARSON_CORRELATION_THRESHOLD:
                severity = SeverityEngine.calculate_correlation_severity(pair.coefficient)
                evidence = EvidenceBuilder.build_correlation_pair_evidence(
                    pair=pair,
                    threshold=PEARSON_CORRELATION_THRESHOLD
                )
                slug_pair = _slugify(f"{pair.column_1}-{pair.column_2}")

                obs = (
                    ScientificObservationBuilder()
                    .with_id(f"obs-corr-{slug_pair}-{report.dataset_id}")
                    .with_category(ObservationCategory.CORRELATION)
                    .with_title(f"Multicollinearity: '{pair.column_1}' & '{pair.column_2}' (r = {pair.coefficient:+.2f})")
                    .with_summary(
                        f"Features '{pair.column_1}' and '{pair.column_2}' exhibit severe pairwise "
                        f"Pearson correlation (r = {pair.coefficient:+.2f}, |r| >= {PEARSON_CORRELATION_THRESHOLD})."
                    )
                    .with_affected_columns([pair.column_1, pair.column_2])
                    .with_severity(severity)
                    .with_confidence(DEFAULT_CONFIDENCE)
                    .with_evidence(evidence)
                    .with_recommendations([
                        f"Prune one of the redundant features ('{pair.column_1}' or '{pair.column_2}') to mitigate multicollinearity."
                    ])
                    .build()
                )
                observations.append(obs)

        return observations

    @classmethod
    def map_noise(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Noise Profiler."""
        observations: List[ScientificObservation] = []
        noise = report.noise

        for col_name, detail in noise.column_outliers.items():
            if detail.outlier_ratio >= OUTLIER_RATIO_THRESHOLD:
                severity = SeverityEngine.calculate_outlier_severity(detail.outlier_ratio)
                evidence = EvidenceBuilder.build_outlier_column_evidence(
                    column_name=col_name,
                    detail=detail,
                    threshold=OUTLIER_RATIO_THRESHOLD
                )
                slug_col = _slugify(col_name)

                obs = (
                    ScientificObservationBuilder()
                    .with_id(f"obs-noise-{slug_col}-{report.dataset_id}")
                    .with_category(ObservationCategory.NOISE)
                    .with_title(f"Statistical Outliers in Column '{col_name}' ({detail.outlier_count} outliers, {detail.outlier_ratio:.1%})")
                    .with_summary(
                        f"Column '{col_name}' contains {detail.outlier_count:,} statistical outliers "
                        f"({detail.outlier_ratio:.1%}) outside IQR bounds [{detail.lower_bound:.2f}, {detail.upper_bound:.2f}]."
                    )
                    .with_affected_columns([col_name])
                    .with_severity(severity)
                    .with_confidence(DEFAULT_CONFIDENCE)
                    .with_evidence(evidence)
                    .with_recommendations([
                        f"Apply Winsorization or quantile clipping on column '{col_name}' to restrict extreme noise."
                    ])
                    .build()
                )
                observations.append(obs)

        return observations

    @classmethod
    def map_feature_quality(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Extract ScientificObservations from the Feature Quality Profiler."""
        observations: List[ScientificObservation] = []
        fq = report.feature_quality

        # 1. Zero Variance Constant Columns
        if fq.constant_columns:
            severity = SeverityEngine.calculate_constant_column_severity()
            evidence = EvidenceBuilder.build_constant_column_evidence(fq.constant_columns)

            obs = (
                ScientificObservationBuilder()
                .with_id(f"obs-fq-constant-{report.dataset_id}")
                .with_category(ObservationCategory.FEATURE_QUALITY)
                .with_title(f"Zero-Variance Constant Columns ({len(fq.constant_columns)} columns)")
                .with_summary(
                    f"Dataset contains {len(fq.constant_columns)} constant column(s) with zero variance: "
                    f"{', '.join(fq.constant_columns)}."
                )
                .with_affected_columns(fq.constant_columns)
                .with_severity(severity)
                .with_confidence(DEFAULT_CONFIDENCE)
                .with_evidence(evidence)
                .with_recommendations([
                    "Drop constant columns as they provide zero predictive variance for model training."
                ])
                .build()
            )
            observations.append(obs)

        # 2. ID-Like Columns
        if fq.id_like_columns:
            severity = SeverityEngine.calculate_id_like_column_severity()
            evidence = EvidenceBuilder.build_id_like_column_evidence(fq.id_like_columns)

            obs = (
                ScientificObservationBuilder()
                .with_id(f"obs-fq-idlike-{report.dataset_id}")
                .with_category(ObservationCategory.FEATURE_QUALITY)
                .with_title(f"High-Cardinality Unique Identifier Columns ({len(fq.id_like_columns)} columns)")
                .with_summary(
                    f"Dataset contains {len(fq.id_like_columns)} column(s) with 100% unique string IDs: "
                    f"{', '.join(fq.id_like_columns)}."
                )
                .with_affected_columns(fq.id_like_columns)
                .with_severity(severity)
                .with_confidence(HEURISTIC_CONFIDENCE)
                .with_evidence(evidence)
                .with_recommendations([
                    "Exclude unique identifier string columns prior to downstream machine learning."
                ])
                .build()
            )
            observations.append(obs)

        return observations

    @classmethod
    def map_all(cls, report: GenomeReportResponse) -> List[ScientificObservation]:
        """Execute all profiler mappers and aggregate observations."""
        all_obs: List[ScientificObservation] = []
        all_obs.extend(cls.map_completeness(report))
        all_obs.extend(cls.map_consistency(report))
        all_obs.extend(cls.map_balance(report))
        all_obs.extend(cls.map_correlation(report))
        all_obs.extend(cls.map_noise(report))
        all_obs.extend(cls.map_feature_quality(report))
        return all_obs

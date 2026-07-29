"""
services/autoscientist/observation_engine.py — Core Observation Engine Coordinator.

Coordinates empirical anomaly extraction across Genome Reports, transforms
profiler outputs into validated ScientificObservation objects, and provides
fallback handling for statistically clean datasets.
"""

import logging
from typing import List

from schemas.intelligence import GenomeReportResponse
from services.autoscientist.observation_builder import ScientificObservationBuilder
from services.autoscientist.observation_constants import DEFAULT_CONFIDENCE, ObservationCategory
from services.autoscientist.observation_mapper import ObservationMapper
from services.autoscientist.observation_models import ScientificObservation

logger = logging.getLogger("dataset_genome.observation_engine")


class ObservationEngine:
    """
    Core Observation Engine for Dataset Genome.
    
    Transforms raw Sprint 2 GenomeReportResponse JSON objects into canonical,
    calibrated ScientificObservation models suitable for downstream problem ranking
    and scientific hypothesis generation.
    """

    def __init__(self) -> None:
        self._mapper = ObservationMapper()

    def process_report(self, report: GenomeReportResponse) -> List[ScientificObservation]:
        """
        Process a GenomeReportResponse and return a list of extracted ScientificObservation models.
        
        If no statistical anomalies are detected across all 6 profiler categories,
        returns a default 'DATASET_STATISTICALLY_OPTIMAL' scientific observation.
        """
        logger.info(f"Processing GenomeReportResponse for dataset_id={report.dataset_id}")

        # 1. Map raw profiler metrics to ScientificObservations
        observations = self._mapper.map_all(report)

        # 2. Fallback for completely healthy datasets with 0 anomalies
        if not observations:
            logger.info(f"Dataset {report.dataset_id} exhibits 0 anomalies. Emitting optimal dataset observation.")
            optimal_obs = (
                ScientificObservationBuilder()
                .with_id(f"obs-healthy-{report.dataset_id}")
                .with_category(ObservationCategory.FEATURE_QUALITY)
                .with_title("Dataset is Statistically Optimal")
                .with_summary(
                    f"Dataset '{report.filename}' exhibits no critical statistical anomalies across all 6 profiler axes. "
                    f"Overall Health Score is {report.health_score.overall_score:.1f}/100 ({report.health_score.grade})."
                )
                .with_affected_columns([])
                .with_severity(0.0)
                .with_confidence(DEFAULT_CONFIDENCE)
                .with_evidence({
                    "overall_health_score": report.health_score.overall_score,
                    "grade": report.health_score.grade,
                    "total_rows": report.num_rows,
                    "total_cols": report.num_cols,
                })
                .with_recommendations([
                    "No corrective dataset mutations are required. Dataset is ready for model training."
                ])
                .with_metadata({"is_statistically_optimal": True})
                .build()
            )
            return [optimal_obs]

        # 3. Sort observations in descending order of severity
        observations.sort(key=lambda obs: obs.severity, reverse=True)
        logger.info(f"Extracted {len(observations)} scientific observations for dataset {report.dataset_id}")
        return observations

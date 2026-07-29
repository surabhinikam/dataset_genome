"""
services/autoscientist/memory_engine.py — Main Scientific Memory Engine Coordinator.

Coordinates experiment encoding, similarity search, confidence calibration history,
historical retrieval, transformation success statistics, and recipe recommendations.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from services.autoscientist.evaluation_constants import EvaluationOutcome, EvaluationRecommendation
from services.autoscientist.evaluation_models import EvaluationReport
from services.autoscientist.memory_constants import DEFAULT_SUCCESS_THRESHOLD, SimilarityMetric
from services.autoscientist.memory_encoder import MemoryEncoder
from services.autoscientist.memory_models import (
    MemoryRecord,
    MemoryRetrievalResult,
    MemorySearchRequest,
)
from services.autoscientist.memory_similarity import SimilarityEngineFactory
from services.autoscientist.memory_store import BaseMemoryStore, LocalMemoryStore
from services.autoscientist.memory_validator import MemoryValidator

logger = logging.getLogger("dataset_genome.memory_engine")


class ScientificMemoryEngine:
    """
    Core Scientific Memory Engine for Dataset Genome AutoScientist.
    
    Enables the system to learn from past experiment evaluation outcomes,
    calculate feature vector similarity, maintain transformation success rates,
    and generate high-confidence experimental recipes.
    """

    def __init__(self, store: Optional[BaseMemoryStore] = None) -> None:
        self._store = store or LocalMemoryStore()
        self._validator = MemoryValidator()
        self._encoder = MemoryEncoder()

    def store_evaluation_report(
        self,
        report: EvaluationReport,
        dataset_id: Optional[UUID] = None,
        transformation_type: Optional[str] = None,
        category: str = "completeness",
        tags: Optional[List[str]] = None,
    ) -> MemoryRecord:
        """
        Encode an EvaluationReport into a MemoryRecord and persist it into the memory store.
        """
        logger.info(f"Storing EvaluationReport '{report.evaluation_id}' in Scientific Memory Engine.")

        # 1. Validate EvaluationReport input
        self._validator.validate_evaluation_report(report)

        # 2. Encode EvaluationReport to canonical MemoryRecord
        record = self._encoder.create_memory_record(
            report=report,
            dataset_id=dataset_id,
            transformation_type=transformation_type,
            category=category,
            tags=tags,
        )

        # 3. Validate MemoryRecord schema & dimensions
        self._validator.validate_record(record)

        # 4. Save to persistence store
        saved_record = self._store.save_record(record)
        logger.info(f"Successfully stored MemoryRecord (id='{saved_record.record_id}') for experiment '{report.experiment_id}'.")
        return saved_record

    def get_memory_record(self, record_id: str) -> Optional[MemoryRecord]:
        """
        Retrieve a MemoryRecord by record_id.
        """
        return self._store.get_record(record_id)

    def search_similar_experiments(self, request: MemorySearchRequest) -> MemoryRetrievalResult:
        """
        Search historical MemoryRecords using vector similarity metrics and filters.
        """
        logger.info(f"Searching memory engine with metric='{request.metric.value}', top_k={request.top_k}")

        # 1. Validate search request parameters
        self._validator.validate_search_request(request)

        # 2. Extract query vector
        query_vector: List[float] = []
        if request.query_vector:
            query_vector = request.query_vector
        elif request.evaluation_report:
            query_vector = self._encoder.encode_feature_vector(request.evaluation_report)
        else:
            # Default reference vector representing ideal high-improvement experiment
            query_vector = [0.80, 0.95, 0.05, 0.05, 0.00, 0.00, 1.0, 1.0]

        # 3. Filter candidates by category or transformation_type
        candidates = self._store.list_records(
            category=request.category,
            transformation_type=request.transformation_type,
        )

        if not candidates:
            logger.info("No candidates found matching memory search criteria.")
            return MemoryRetrievalResult(
                query_record_id=request.evaluation_report.evaluation_id if request.evaluation_report else None,
                similar_records=[],
                similarity_scores=[],
                historical_success_rate=0.50,
                recommended_transformation=None,
                blacklisted_transformations=[],
                confidence_calibration_adjustment=0.0,
            )

        # 4. Execute vector similarity search
        similarity_engine = SimilarityEngineFactory.get_engine(request.metric)
        candidate_vectors = [(rec.record_id, rec.feature_vector) for rec in candidates if rec.feature_vector]

        ranked_pairs = similarity_engine.rank_similar_vectors(
            query_vector=query_vector,
            candidate_vectors=candidate_vectors,
            top_k=request.top_k,
        )

        record_map = {rec.record_id: rec for rec in candidates}
        matched_records: List[MemoryRecord] = []
        scores: List[float] = []

        for rec_id, score in ranked_pairs:
            if rec_id in record_map:
                matched_records.append(record_map[rec_id])
                scores.append(score)

        # 5. Compute historical success statistics & recommendations
        success_rate = self._compute_success_rate(matched_records)
        recommended_trans = self._select_recommended_transformation(matched_records)
        blacklisted = self._identify_blacklisted_transformations(candidates)
        calibration_adj = self._compute_confidence_adjustment(matched_records)

        return MemoryRetrievalResult(
            query_record_id=request.evaluation_report.evaluation_id if request.evaluation_report else None,
            similar_records=matched_records,
            similarity_scores=scores,
            historical_success_rate=success_rate,
            recommended_transformation=recommended_trans,
            blacklisted_transformations=blacklisted,
            confidence_calibration_adjustment=calibration_adj,
        )

    def get_transformation_stats(self, transformation_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Compute global or transformation-specific success statistics.
        """
        records = self._store.list_records(transformation_type=transformation_type)
        if not records:
            return {
                "transformation_type": transformation_type or "all",
                "total_experiments": 0,
                "verified_count": 0,
                "failed_count": 0,
                "success_rate": 0.0,
                "mean_actual_improvement": 0.0,
                "mean_prediction_error": 0.0,
            }

        total = len(records)
        verified = sum(1 for r in records if r.overall_result in (EvaluationOutcome.VERIFIED, EvaluationOutcome.PARTIALLY_VERIFIED))
        failed = sum(1 for r in records if r.overall_result == EvaluationOutcome.FAILED)
        mean_actual = sum(r.actual_improvement for r in records) / total
        mean_error = sum(r.prediction_error for r in records) / total

        return {
            "transformation_type": transformation_type or "all",
            "total_experiments": total,
            "verified_count": verified,
            "failed_count": failed,
            "success_rate": round(verified / total, 4),
            "mean_actual_improvement": round(mean_actual, 4),
            "mean_prediction_error": round(mean_error, 4),
        }

    def generate_recipe_recommendations(self, category: str = "completeness") -> Dict[str, Any]:
        """
        Generate high-confidence experimental recipes for a profiler category based on memory.
        """
        records = self._store.list_records(category=category)
        success_rate = self._compute_success_rate(records)
        recommended = self._select_recommended_transformation(records)
        blacklisted = self._identify_blacklisted_transformations(records)

        recipes: List[str] = []
        if recommended:
            recipes.append(f"Recommended mutation recipe: Apply '{recommended}' for category '{category}'.")
        else:
            recipes.append(f"Apply standard median imputation recipe for category '{category}'.")

        return {
            "category": category,
            "historical_success_rate": success_rate,
            "recommended_recipes": recipes,
            "blacklisted_transformations": blacklisted,
        }

    def _compute_success_rate(self, records: List[MemoryRecord]) -> float:
        if not records:
            return 0.50
        successful = sum(1 for r in records if r.actual_improvement >= DEFAULT_SUCCESS_THRESHOLD and r.overall_result != EvaluationOutcome.FAILED)
        return round(successful / len(records), 4)

    def _select_recommended_transformation(self, records: List[MemoryRecord]) -> Optional[str]:
        if not records:
            return None
        trans_improvements: Dict[str, List[float]] = {}
        for r in records:
            if r.overall_result != EvaluationOutcome.FAILED:
                trans_improvements.setdefault(r.transformation_type, []).append(r.actual_improvement)

        if not trans_improvements:
            return None

        best_trans = max(trans_improvements.keys(), key=lambda t: sum(trans_improvements[t]) / len(trans_improvements[t]))
        return best_trans

    def _identify_blacklisted_transformations(self, records: List[MemoryRecord]) -> List[str]:
        blacklisted: List[str] = []
        trans_outcomes: Dict[str, List[EvaluationOutcome]] = {}
        for r in records:
            trans_outcomes.setdefault(r.transformation_type, []).append(r.overall_result)

        for trans_name, outcomes in trans_outcomes.items():
            failed_count = sum(1 for o in outcomes if o == EvaluationOutcome.FAILED)
            if len(outcomes) >= 2 and (failed_count / len(outcomes)) >= 0.75:
                blacklisted.append(trans_name)

        return blacklisted

    def _compute_confidence_adjustment(self, records: List[MemoryRecord]) -> float:
        if not records:
            return 0.0
        avg_calib = sum(r.confidence_calibration for r in records) / len(records)
        return round(avg_calib, 4)

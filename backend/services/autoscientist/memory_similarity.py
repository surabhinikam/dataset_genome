"""
services/autoscientist/memory_similarity.py — Pluggable Similarity Engines for Memory Search.

Provides abstract BaseSimilarityEngine interface along with Cosine and Euclidean
similarity implementations. Designed for seamless swap with vector databases.
"""

import math
from abc import ABC, abstractmethod
from typing import List, Tuple
from services.autoscientist.memory_constants import SimilarityMetric


class BaseSimilarityEngine(ABC):
    """
    Abstract interface for computing vector similarity scores.
    
    Future Vector DB integrations (Chroma, Qdrant, Pinecone) will inherit from this
    class to maintain uniform API contracts across local and distributed deployments.
    """

    @abstractmethod
    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute similarity score between two numerical feature vectors in [0.0..1.0].
        """
        pass

    @abstractmethod
    def rank_similar_vectors(
        self,
        query_vector: List[float],
        candidate_vectors: List[Tuple[str, List[float]]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Rank candidate vectors by similarity score to query_vector.
        
        Returns List of (candidate_id, similarity_score) sorted descending by score.
        """
        pass


class CosineSimilarityEngine(BaseSimilarityEngine):
    """Cosine similarity engine operating on normalized feature vectors."""

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_v1 = math.sqrt(sum(a * a for a in vec1))
        norm_v2 = math.sqrt(sum(b * b for b in vec2))

        if norm_v1 == 0.0 or norm_v2 == 0.0:
            return 0.0

        cosine_sim = dot_product / (norm_v1 * norm_v2)
        # Normalize from [-1.0, 1.0] to [0.0, 1.0]
        normalized_sim = (cosine_sim + 1.0) / 2.0
        return round(max(0.0, min(1.0, normalized_sim)), 4)

    def rank_similar_vectors(
        self,
        query_vector: List[float],
        candidate_vectors: List[Tuple[str, List[float]]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        scores: List[Tuple[str, float]] = []
        for cand_id, vec in candidate_vectors:
            score = self.calculate_similarity(query_vector, vec)
            scores.append((cand_id, score))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]


class EuclideanSimilarityEngine(BaseSimilarityEngine):
    """Euclidean distance-based similarity engine (1 / (1 + distance))."""

    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
        similarity = 1.0 / (1.0 + distance)
        return round(max(0.0, min(1.0, similarity)), 4)

    def rank_similar_vectors(
        self,
        query_vector: List[float],
        candidate_vectors: List[Tuple[str, List[float]]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        scores: List[Tuple[str, float]] = []
        for cand_id, vec in candidate_vectors:
            score = self.calculate_similarity(query_vector, vec)
            scores.append((cand_id, score))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]


class SimilarityEngineFactory:
    """Factory for instantiating similarity engines by SimilarityMetric enum."""

    @classmethod
    def get_engine(cls, metric: SimilarityMetric = SimilarityMetric.COSINE) -> BaseSimilarityEngine:
        if metric == SimilarityMetric.EUCLIDEAN:
            return EuclideanSimilarityEngine()
        return CosineSimilarityEngine()

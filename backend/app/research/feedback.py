"""
backend/app/research/feedback.py — Research Feedback Engine.

Converts improvement recommendations into dataset evolution requests.
Tracks version progression (from_version -> to_version), expected improvement, and observed improvement.
"""

import logging
import uuid
from typing import List, Optional

from app.research.models import ResearchImprovementRequest, ResearchRecommendation

logger = logging.getLogger("dataset_genome.research.feedback")


class ResearchFeedbackEngine:
    """
    Converts recommendations into formal dataset evolution requests and tracks score deltas.
    """

    def create_improvement_request(
        self,
        from_version: str,
        to_version: str,
        recommendations: List[ResearchRecommendation],
    ) -> ResearchImprovementRequest:
        """
        Package recommendations into a structured ResearchImprovementRequest.
        """
        req_id = f"req-feed-{uuid.uuid4().hex[:6]}"
        expected_gain = sum(r.expected_score_gain for r in recommendations)

        req = ResearchImprovementRequest(
            request_id=req_id,
            from_version=from_version,
            to_version=to_version,
            applied_recommendations=recommendations,
            expected_improvement=round(expected_gain, 2),
        )

        logger.info(f"ResearchFeedbackEngine created request '{req_id}' ({from_version} -> {to_version}, Expected Gain: +{expected_gain:.1f}).")
        return req

    def record_observed_improvement(
        self,
        request: ResearchImprovementRequest,
        previous_score: float,
        current_score: float,
    ) -> float:
        """
        Calculate and record actual observed score improvement delta.
        """
        delta = round(current_score - previous_score, 2)
        request.observed_improvement = delta
        logger.info(f"ResearchFeedbackEngine recorded observed delta for '{request.request_id}': {delta:+.2f} (Expected: +{request.expected_improvement:.2f}).")
        return delta

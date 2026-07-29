"""
services/autoscientist/memory_constants.py — Constants & Enums for Scientific Memory Engine.

Defines similarity metric enums, feature vector dimensions, default threshold parameters,
and recommendation weight constants for the Scientific Memory Engine.
"""

from enum import Enum


class SimilarityMetric(str, Enum):
    """Supported similarity distance metrics for experiment vector comparison."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    JACCARD = "jaccard"


# Feature Vector Dimensions (8D Representation)
# [0] health_before / 100.0
# [1] health_after / 100.0
# [2] predicted_improvement
# [3] actual_improvement
# [4] prediction_error
# [5] confidence_calibration
# [6] hypothesis_verified (1.0 if True else 0.0)
# [7] recommendation_weight (1.0 for PROCEED, 0.5 for REVISE, 0.0 for ROLLBACK)
FEATURE_VECTOR_DIMENSION = 8

# Default Similarity Thresholds
DEFAULT_TOP_K = 5
MIN_SIMILARITY_THRESHOLD = 0.50
DEFAULT_SUCCESS_THRESHOLD = 0.02  # Actual improvement >= 0.02 is considered successful

# Persistence Settings
DEFAULT_MEMORY_FILE_NAME = "memory_store.json"

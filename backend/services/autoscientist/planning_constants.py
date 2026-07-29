"""
services/autoscientist/planning_constants.py — Constants for Experiment Planner.

Defines default resource bounds, complexity levels, and default execution constraints.
"""

from enum import Enum
from typing import Dict, List


class PlanningComplexity(str, Enum):
    """Complexity levels for planned dataset experiments."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# Default System Constraints for Execution
DEFAULT_EXECUTION_CONSTRAINTS: List[str] = [
    "Run within isolated sandboxed process environment.",
    "Do not mutate baseline CSV file in-place; write to new versioned path.",
    "Enforce RAM usage limit of 2048 MB.",
    "Enforce maximum execution timeout of 60 seconds."
]

# Baseline Resource Multipliers (per 1,000 rows)
BASE_RUNTIME_PER_1K_ROWS: Dict[str, float] = {
    "FeatureDropTransformation": 0.05,
    "RowDeduplicationTransformation": 0.10,
    "TypeUnificationTransformation": 0.15,
    "FeaturePruningTransformation": 0.10,
    "MedianImputationTransformation": 0.20,
    "ImputationTransformation": 0.80,        # KNN Imputation
    "WinsorizationTransformation": 0.25,
    "ClassRebalancingTransformation": 1.20,    # SMOTE
}

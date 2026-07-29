"""
services/autoscientist/priority_queue.py — Deterministic Priority Queue with Multi-Criteria Tie Breaking.

Enforces strict tie-breaking rules to guarantee deterministic ordering across runs:
  1. Utility score (descending)
  2. Severity (descending)
  3. Repair Complexity (ascending)
  4. Alphabetical Category name (ascending)
  5. Stable unique ID ordering (ascending)
"""

from typing import List, Optional
from uuid import UUID

from services.autoscientist.ranking_models import PrioritizedProblemQueue, RankedProblem


class DeterministicPriorityQueue:
    """
    Manages building and sorting a PrioritizedProblemQueue with deterministic tie-breaking logic.
    """

    @staticmethod
    def _sort_key(problem: RankedProblem):
        """
        Sort key tuple for deterministic ordering.
        Python sort operates ascendingly, so negate descending float values.
        """
        return (
            -problem.utility_score,                            # 1. Utility score (descending)
            -problem.component_scores.severity,               # 2. Severity (descending)
            problem.component_scores.repair_complexity,        # 3. Repair complexity (ascending)
            problem.observation.category.value,               # 4. Alphabetical category (ascending)
            problem.observation.id,                           # 5. Observation ID (ascending stable sort)
        )

    @classmethod
    def create_queue(
        cls,
        ranked_problems: List[RankedProblem],
        dataset_id: Optional[UUID] = None
    ) -> PrioritizedProblemQueue:
        """
        Sort ranked problems deterministically and assign 1-indexed ranks.
        """
        # Sort deterministically
        sorted_problems = sorted(ranked_problems, key=cls._sort_key)

        # Re-assign 1-indexed ranks after sorting
        reindexed_problems: List[RankedProblem] = []
        for idx, item in enumerate(sorted_problems, start=1):
            updated_item = item.model_copy(update={"rank": idx})
            reindexed_problems.append(updated_item)

        highest = reindexed_problems[0] if reindexed_problems else None

        return PrioritizedProblemQueue(
            dataset_id=dataset_id,
            total_problems=len(reindexed_problems),
            ranked_problems=reindexed_problems,
            highest_priority_problem=highest,
        )

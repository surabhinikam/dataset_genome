"""
services/autoscientist/ranking_engine.py — Main Problem Ranking Engine Coordinator.

Transforms raw ScientificObservation objects into a deterministic PrioritizedProblemQueue.
"""

import logging
from typing import List, Optional
from uuid import UUID

from services.autoscientist.observation_models import ScientificObservation
from services.autoscientist.priority_queue import DeterministicPriorityQueue
from services.autoscientist.ranking_explainer import RankingExplainer
from services.autoscientist.ranking_models import PrioritizedProblemQueue, RankedProblem
from services.autoscientist.utility_functions import UtilityCalculator

logger = logging.getLogger("dataset_genome.ranking_engine")


class ProblemRankingEngine:
    """
    Problem Ranking Engine for Dataset Genome.
    
    Ranks dataset flaws by computing continuous multi-criteria utility scores
    combining severity, information loss risk, impact potential, and repair complexity.
    """

    def __init__(self) -> None:
        self._calculator = UtilityCalculator()
        self._explainer = RankingExplainer()
        self._queue_builder = DeterministicPriorityQueue()

    def rank_observations(
        self,
        observations: List[ScientificObservation],
        dataset_id: Optional[UUID] = None
    ) -> PrioritizedProblemQueue:
        """
        Rank a list of ScientificObservation objects into a PrioritizedProblemQueue.
        
        Handles empty input lists gracefully by returning an empty queue.
        Enforces strict multi-criteria tie-breaking for deterministic output ordering.
        """
        logger.info(f"Ranking {len(observations)} observations for dataset_id={dataset_id}")

        if not observations:
            logger.info("Empty observations list provided to ProblemRankingEngine.")
            return self._queue_builder.create_queue(ranked_problems=[], dataset_id=dataset_id)

        ranked_problems: List[RankedProblem] = []

        for idx, obs in enumerate(observations, start=1):
            # 1. Compute multi-criteria utility component scores
            components = self._calculator.compute_components(obs)

            # 2. Compute scalar utility score U(O_i)
            utility_score = self._calculator.compute_utility_score(obs, components)

            # 3. Synthesize natural language explanation & next step
            explanation = self._explainer.generate_explanation(obs, utility_score, components)
            next_step = self._explainer.generate_recommended_next_step(obs)

            # 4. Construct temporary RankedProblem item
            problem = RankedProblem(
                rank=idx,
                observation_id=obs.id,
                observation=obs,
                utility_score=utility_score,
                component_scores=components,
                explanation=explanation,
                recommended_next_step=next_step,
            )
            ranked_problems.append(problem)

        # 5. Deterministically sort and build final queue
        queue = self._queue_builder.create_queue(ranked_problems=ranked_problems, dataset_id=dataset_id)
        logger.info(f"Successfully constructed PrioritizedProblemQueue with {queue.total_problems} problem(s).")
        return queue

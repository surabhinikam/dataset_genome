"""
backend/app/adaptive_data/agents/balancer.py — AGENT 3: Dataset Balancer.

Analyzes sample distribution across domains, difficulty levels, and experiment types.
Detects imbalance and formulates target sample generation recommendations. Generates BalanceReport.
"""

import logging
from typing import Dict, List
from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import BalanceReport, TargetSampleRecommendation
from app.dataset_generator.models import ScientificReasoningRecord

logger = logging.getLogger("dataset_genome.adaptive_data.balancer")


class DatasetBalancer:
    """
    AGENT 3 — Dataset Balancer.
    
    Evaluates dataset domain parity, difficulty representation, and experiment type distribution.
    """

    ALL_BENCHMARK_DOMAINS = ["Agriculture", "Medicine", "Climate Science", "Physics", "Chemistry", "Biology"]

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def balance(self, records: List[ScientificReasoningRecord]) -> BalanceReport:
        """
        Analyze dataset distributions and detect imbalances.
        """
        logger.info(f"Agent 3 (Balancer) analyzing distributions across {len(records)} sample(s)...")

        total_samples = len(records)
        domain_dist: Dict[str, int] = {}
        difficulty_dist: Dict[str, int] = {}
        exp_type_dist: Dict[str, int] = {}

        for r in records:
            domain_dist[r.domain] = domain_dist.get(r.domain, 0) + 1
            difficulty_dist[r.difficulty] = difficulty_dist.get(r.difficulty, 0) + 1

            exp = (r.experiment_design or "").lower()
            if "clinical" in exp or "patient" in exp:
                exp_type_dist["clinical_trial"] = exp_type_dist.get("clinical_trial", 0) + 1
            elif "laboratory" in exp or "in vitro" in exp:
                exp_type_dist["laboratory_experiment"] = exp_type_dist.get("laboratory_experiment", 0) + 1
            elif "simulation" in exp or "modeling" in exp:
                exp_type_dist["simulation_study"] = exp_type_dist.get("simulation_study", 0) + 1
            else:
                exp_type_dist["observational_study"] = exp_type_dist.get("observational_study", 0) + 1

        recommendations: List[TargetSampleRecommendation] = []
        imbalance_detected = False

        if total_samples > 0:
            # 1. Check for Domain Imbalance & Missing Domains
            for domain in self.ALL_BENCHMARK_DOMAINS:
                cnt = domain_dist.get(domain, 0)
                ratio = cnt / total_samples
                if cnt == 0:
                    imbalance_detected = True
                    recommendations.append(
                        TargetSampleRecommendation(
                            target_domain=domain,
                            target_difficulty="medium",
                            recommended_count=15,
                            reason=f"Domain '{domain}' is absent from dataset. Generate baseline samples.",
                        )
                    )
                elif ratio < 0.10:
                    imbalance_detected = True
                    recommendations.append(
                        TargetSampleRecommendation(
                            target_domain=domain,
                            target_difficulty="medium",
                            recommended_count=10,
                            reason=f"Domain '{domain}' is underrepresented ({cnt} samples, {ratio * 100:.1f}%).",
                        )
                    )

            # 2. Check for Difficulty Imbalance (Hard < 30%)
            hard_cnt = difficulty_dist.get("hard", 0)
            hard_ratio = hard_cnt / total_samples
            if hard_ratio < self.config.target_hard_sample_ratio:
                imbalance_detected = True
                needed = int(round(total_samples * self.config.target_hard_sample_ratio)) - hard_cnt
                recommendations.append(
                    TargetSampleRecommendation(
                        target_domain="Multi-Domain",
                        target_difficulty="hard",
                        recommended_count=max(5, needed),
                        reason=f"Hard samples constitute only {hard_ratio * 100:.1f}% of dataset (Target >= 30%).",
                    )
                )

        # Calculate Balance Score (0-100)
        domain_parity = len(domain_dist) / len(self.ALL_BENCHMARK_DOMAINS)
        hard_parity = min(1.0, (difficulty_dist.get("hard", 0) / max(1, total_samples)) / self.config.target_hard_sample_ratio)
        
        balance_score = round((0.60 * domain_parity + 0.40 * hard_parity) * 100.0, 2)

        report = BalanceReport(
            domain_distribution=domain_dist,
            difficulty_distribution=difficulty_dist,
            experiment_type_distribution=exp_type_dist,
            imbalance_detected=imbalance_detected,
            balance_score=min(100.0, max(0.0, balance_score)),
            target_sample_recommendations=recommendations,
        )

        logger.info(
            f"Agent 3 (Balancer) completed: Balance score: {balance_score}/100 "
            f"(Imbalance detected: {imbalance_detected}, {len(recommendations)} target recommendation(s))."
        )
        return report

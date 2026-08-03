"""
backend/app/benchmark/generator.py — Domain-Specific Generator for Official Benchmark v1.0.

Generates scientifically rigorous BenchmarkSample instances using BenchmarkSampleBuilder
across 10 supported domains and 4 balanced difficulty levels.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.benchmark.models import BenchmarkSample, BenchmarkSampleBuilder

logger = logging.getLogger("dataset_genome.benchmark.generator")

SUPPORTED_DOMAINS = [
    "Agriculture",
    "Healthcare",
    "Climate Science",
    "Biology",
    "Chemistry",
    "Physics",
    "Mathematics",
    "Finance",
    "HR",
    "Market Analysis",
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard", "Expert"]


from app.benchmark.diversity_engine import DOMAIN_DIVERSITY_POOLS, ScientificDiversityEngine
from app.benchmark.quality_scorer import BenchmarkQualityScorer

REASONING_STYLES_LIST = [
    "Positive Result", "Negative Result", "Ambiguous Result",
    "Conflicting Literature", "Failed Experiment", "Replication Study",
    "Unexpected Observation"
]


class BenchmarkGenerator:
    """
    Generator engine synthesizing official Dataset Genome Benchmark samples
    across 10 scientific domains, 4 difficulty levels, and 7 reasoning styles.
    """

    def __init__(self) -> None:
        self.diversity_engine = ScientificDiversityEngine()

    def generate_sample(
        self,
        domain: str = "Agriculture",
        difficulty: str = "Medium",
        index: int = 1,
        reasoning_style: Optional[str] = None,
    ) -> BenchmarkSample:
        """
        Generate a single complete 16-field BenchmarkSample using BenchmarkSampleBuilder.
        """
        if domain not in SUPPORTED_DOMAINS:
            domain = "Agriculture"
        if difficulty not in DIFFICULTY_LEVELS:
            difficulty = "Medium"

        if not reasoning_style or reasoning_style not in REASONING_STYLES_LIST:
            reasoning_style = REASONING_STYLES_LIST[(index - 1) % len(REASONING_STYLES_LIST)]

        sample_id = f"bm-{domain.lower().replace(' ', '-')[:6]}-{difficulty.lower()[:3]}-{index:03d}-{uuid.uuid4().hex[:4]}"

        # Domain template data
        templates = self._get_domain_templates(domain, difficulty, reasoning_style, index)

        builder = BenchmarkSampleBuilder(sample_id=sample_id, domain=domain, difficulty=difficulty)
        builder.set_reasoning_style(reasoning_style)
        builder.set_inquiry(
            prompt=templates["prompt"],
            context=templates["context"],
            observation=templates["observation"],
        )
        builder.set_problem(
            problem_identification=templates["problem"],
            research_gap=templates["research_gap"],
        )
        builder.set_hypotheses(
            primary=templates["primary_hypothesis"],
            alternative=templates["alternative_hypothesis"],
        )
        builder.set_experiment(
            design=templates["experiment_design"],
            metrics=templates["evaluation_metrics"],
            expected_results=templates["expected_results"],
            failure_cases=templates["failure_cases"],
        )
        builder.set_conclusion(scientific_conclusion=templates["scientific_conclusion"])
        builder.set_metadata({
            "generated_by": "DatasetGenomeBenchmarkGenerator-v1.0",
            "domain_category": domain,
            "difficulty_rating": difficulty,
            "reasoning_style": reasoning_style,
            "benchmark_version": "v1.0",
        })

        sample = builder.build()
        sample = BenchmarkQualityScorer.attach_quality_scores(sample)
        return sample

    def generate_benchmark_suite(
        self,
        samples_per_domain: int = 4,
        domains: Optional[List[str]] = None,
    ) -> List[BenchmarkSample]:
        """
        Generate a complete benchmark dataset suite balanced across domains, difficulty levels, and reasoning styles.
        """
        target_domains = domains or SUPPORTED_DOMAINS
        logger.info(
            f"BenchmarkGenerator synthesizing benchmark dataset suite for {len(target_domains)} domains "
            f"({samples_per_domain} samples/domain)..."
        )

        samples: List[BenchmarkSample] = []
        global_idx = 0
        for dom in target_domains:
            for idx in range(1, samples_per_domain + 1):
                diff = DIFFICULTY_LEVELS[global_idx % len(DIFFICULTY_LEVELS)]
                style = REASONING_STYLES_LIST[global_idx % len(REASONING_STYLES_LIST)]
                sample = self.generate_sample(domain=dom, difficulty=diff, index=idx, reasoning_style=style)
                samples.append(sample)
                global_idx += 1

        logger.info(f"BenchmarkGenerator successfully generated {len(samples)} benchmark sample(s).")
        return samples

    def _get_domain_templates(self, domain: str, difficulty: str, reasoning_style: str, index: int = 1) -> Dict[str, Any]:
        """Return scientific templates tailored to domain, difficulty level, and reasoning style."""
        pool_item = self.diversity_engine.get_diverse_pool(domain, index)
        topic = pool_item["topic"]
        organism = pool_item["organism"]

        # Difficulty metric counts
        metric_counts = {"Easy": 3, "Medium": 4, "Hard": 5, "Expert": 6}
        num_metrics = metric_counts.get(difficulty, 4)
        base_metrics = pool_item.get("metrics", ["Primary Yield Metric", "Statistical Significance (p)", "Effect Size (d)"])
        metrics = (base_metrics * 2)[:num_metrics]

        # Reasoning style context adjustments
        if reasoning_style == "Negative Result":
            obs = f"Empirical testing revealed no significant shift in {organism} response under target treatment (p = 0.42)."
            exp_res = f"Primary hypothesis disproved; treatment effect remains within null control bounds (Delta < 0.05)."
            scientific_conc = f"Rigorous testing confirms a null relationship, refuting earlier uncalibrated models."
        elif reasoning_style == "Ambiguous Result":
            obs = f"Assay results for {organism} yielded high variance across replicates (95% CI [-0.12, 0.48])."
            exp_res = f"Inconclusive trend observed; secondary power analysis indicates need for 4x larger sample cohort."
            scientific_conc = f"Evidence remains inconclusive, highlighting critical measurement noise and confounding factors."
        elif reasoning_style == "Failed Experiment":
            obs = f"Severe measurement artifact detected due to calibration drift during {topic} assay execution."
            exp_res = f"Experimental trial invalidated by thermal control breakdown at t=24h."
            scientific_conc = f"Trial failed due to physical measurement artifacts, mandating revised experimental protocols."
        elif reasoning_style == "Replication Study":
            obs = f"Replication trial evaluated original landmark findings for {topic} in {organism} under revised controls."
            exp_res = f"Landmark effect reproduced with high fidelity (R² = 0.94, p < 0.001)."
            scientific_conc = f"Replication confirms robust generalizability of the original scientific phenomenon."
        elif reasoning_style == "Unexpected Observation":
            obs = f"Unpredicted secondary peak observed in {organism} transcriptomic expression during {topic} exposure."
            exp_res = f"Primary hypothesis partially supported, but an unexpected alternative pathway emerged."
            scientific_conc = f"Discovery of an unpredicted anomalous mechanism challenges prevailing domain models."
        else:
            obs = f"High-precision measurements of {organism} demonstrate a statistically significant 3.8-fold shift in response."
            exp_res = f"Primary hypothesis supported; key evaluation metrics show > 3.5-fold improvement."
            scientific_conc = f"Target mechanism confirmed as the primary driver of observed empirical phenomena."

        return {
            "prompt": f"Investigate {topic} mechanisms in {domain} ({difficulty} complexity, {reasoning_style} style).",
            "context": pool_item["context"],
            "observation": obs,
            "problem": f"Unclear causal pathway governing {topic} under varying experimental conditions.",
            "research_gap": f"Lack of high-resolution quantitative tracking for {pool_item.get('biomarker', 'key molecular marker')}.",
            "primary_hypothesis": f"Targeted activation of {pool_item.get('biomarker', 'the primary regulatory axis')} governs {topic}.",
            "alternative_hypothesis": f"Observed variations in {topic} are driven by alternative metabolic or environmental feedback loops.",
            "experiment_design": {
                "methodology": pool_item["methodology"],
                "variables": {"independent": "Target Treatment Level", "dependent": metrics[0]},
                "control": "Baseline standard control cohort",
                "sample_size": f"n = {100 if difficulty == 'Expert' else 30} per arm",
            },
            "evaluation_metrics": metrics,
            "expected_results": exp_res,
            "failure_cases": [f"Uncontrolled environmental fluctuation during assay", f"Loss of baseline control specificity"],
            "scientific_conclusion": scientific_conc,
        }

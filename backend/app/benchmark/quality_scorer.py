"""
backend/app/benchmark/quality_scorer.py — Automatic Quality Scoring Engine for Benchmark Samples.

Evaluates each BenchmarkSample across 7 rigorous scientific dimensions (range 0–100):
  1. Scientific Credibility
  2. Novelty
  3. Reasoning Depth
  4. Experiment Complexity
  5. Domain Accuracy
  6. Statistical Rigor
  7. Diversity Contribution

Computes an overall composite quality score and attaches the breakdown to sample metadata.
"""

import math
import re
from typing import Any, Dict, List, Set, Tuple

from app.benchmark.models import BenchmarkSample


_STATISTICAL_KEYWORDS = {
    "p-value", "p <", "p=", "p>", "confidence interval", "95% ci", "standard deviation",
    "power analysis", "n=", "sample size", "anova", "t-test", "hazard ratio", "wilcoxon",
    "regression", "bayesian", "chi-square", "f-stat", "cohen's d", "m-value", "turnover frequency"
}

_DOMAIN_KEYWORDS = {
    "Agriculture": {"crop", "yield", "salinity", "soil", "maize", "stomata", "transporter", "drought", "microbiome", "nitrogen", "photosynthesis", "phenotype"},
    "Healthcare": {"biomarker", "clinical", "insulin", "serum", "cytokine", "oncology", "cardiac", "patient", "therapy", "assay", "pathology", "receptor"},
    "Climate Science": {"aerosol", "cloud", "albedo", "radiative", "stratocumulus", "forcing", "carbon", "temperature", "atmospheric", "climate", "ocean", "sea-level"},
    "Biology": {"crispr", "gene", "protein", "cell", "kinase", "epigenetic", "rna-seq", "smfret", "expression", "molecular", "pathway", "transcription"},
    "Chemistry": {"mof", "catalyst", "photoreduction", "turnover", "synthesis", "ligand", "kinetic", "reaction", "spectroscopy", "molecular", "bond", "valence"},
    "Physics": {"graphene", "quantum", "hall", "chern", "conductance", "topological", "moiré", "superconductivity", "spin", "lattice", "thermodynamic", "photon"},
    "Mathematics": {"pde", "navier-stokes", "sobolev", "vorticity", "enstrophy", "singularity", "theorem", "manifold", "matrix", "bound", "convergence", "eigenvalue"},
    "Finance": {"risk", "liquidity", "algorithmic", "order book", "volatility", "portfolio", "arbitrage", "contagion", "var", "yield curve", "option", "spread"},
    "HR": {"attrition", "network", "centrality", "burnout", "retention", "gnn", "engagement", "turnover", "hazard ratio", "satisfaction", "performance", "team"},
    "Market Analysis": {"consumer", "demand", "inflation", "elasticity", "bayesian", "market share", "stagflation", "pricing", "adoption", "forecast", "revenue", "churn"},
}


class BenchmarkQualityScorer:
    """
    Evaluates individual BenchmarkSample quality across multiple dimensions.
    """

    @staticmethod
    def score_sample(sample: BenchmarkSample, corpus: List[BenchmarkSample] = None) -> Dict[str, float]:
        """
        Compute quality sub-scores and overall quality score for a BenchmarkSample.
        """
        corpus = corpus or []

        # 1. Scientific Credibility (0-100)
        credibility = 70.0
        if sample.primary_hypothesis and len(sample.primary_hypothesis) > 20:
            credibility += 10.0
        if sample.alternative_hypothesis and len(sample.alternative_hypothesis) > 20:
            credibility += 10.0
        design = sample.experiment_design or {}
        if design.get("control") or design.get("variables"):
            credibility += 10.0

        # 2. Reasoning Depth (0-100)
        depth_score = 0.0
        total_text_len = (
            len(sample.prompt) + len(sample.context) + len(sample.observation) +
            len(sample.problem_identification) + len(sample.research_gap) +
            len(sample.scientific_conclusion)
        )
        depth_score = min(100.0, (total_text_len / 600.0) * 100.0)

        # 3. Experiment Complexity (0-100)
        complexity_score = 40.0
        metrics_count = len(sample.evaluation_metrics)
        if metrics_count >= 5:
            complexity_score += 30.0
        elif metrics_count >= 3:
            complexity_score += 20.0
        else:
            complexity_score += 10.0

        if isinstance(design, dict):
            if "variables" in design:
                complexity_score += 15.0
            if "sample_size" in design or "statistical_power" in design:
                complexity_score += 15.0

        # 4. Domain Accuracy (0-100)
        domain_keywords = _DOMAIN_KEYWORDS.get(sample.domain, set())
        sample_text = (
            f"{sample.prompt} {sample.context} {sample.observation} "
            f"{sample.primary_hypothesis} {sample.scientific_conclusion}"
        ).lower()

        matched_kw = sum(1 for kw in domain_keywords if kw in sample_text)
        accuracy_score = min(100.0, 50.0 + (matched_kw * 10.0))

        # 5. Statistical Rigor (0-100)
        matched_stat = sum(1 for kw in _STATISTICAL_KEYWORDS if kw in sample_text)
        rigor_score = min(100.0, 40.0 + (matched_stat * 15.0))

        # 6. Novelty (0-100)
        if corpus:
            sims = []
            sample_words = set(re.findall(r'\w+', sample_text))
            for other in corpus:
                if other.sample_id == sample.sample_id:
                    continue
                other_text = f"{other.prompt} {other.context} {other.primary_hypothesis}".lower()
                other_words = set(re.findall(r'\w+', other_text))
                if sample_words and other_words:
                    jaccard = len(sample_words & other_words) / len(sample_words | other_words)
                    sims.append(jaccard)
            max_sim = max(sims) if sims else 0.0
            novelty_score = max(0.0, (1.0 - max_sim) * 100.0)
        else:
            novelty_score = 85.0

        # 7. Diversity Contribution (0-100)
        diversity_score = 80.0
        if getattr(sample, "reasoning_style", None) in [
            "Negative Result", "Ambiguous Result", "Conflicting Literature",
            "Failed Experiment", "Replication Study", "Unexpected Observation"
        ]:
            diversity_score += 20.0

        diversity_score = min(100.0, diversity_score)

        # Overall Composite Score
        overall = (
            credibility * 0.20 +
            depth_score * 0.15 +
            complexity_score * 0.15 +
            accuracy_score * 0.15 +
            rigor_score * 0.15 +
            novelty_score * 0.10 +
            diversity_score * 0.10
        )

        scores = {
            "scientific_credibility": round(credibility, 2),
            "reasoning_depth": round(depth_score, 2),
            "experiment_complexity": round(complexity_score, 2),
            "domain_accuracy": round(accuracy_score, 2),
            "statistical_rigor": round(rigor_score, 2),
            "novelty": round(novelty_score, 2),
            "diversity_contribution": round(diversity_score, 2),
            "overall_sample_quality": round(overall, 2),
        }

        return scores

    @classmethod
    def attach_quality_scores(cls, sample: BenchmarkSample, corpus: List[BenchmarkSample] = None) -> BenchmarkSample:
        """Attach calculated quality score breakdown to sample metadata."""
        scores = cls.score_sample(sample, corpus)
        sample.metadata["quality_scores"] = scores
        sample.metadata["overall_quality_score"] = scores["overall_sample_quality"]
        return sample

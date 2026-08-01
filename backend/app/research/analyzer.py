"""
backend/app/research/analyzer.py — Research Analyzer Module.

Analyzes model accuracy, reasoning quality, failure patterns, coverage gaps,
weak domains, and experiment weaknesses to determine why the model underperformed.
"""

import logging
from typing import Any, Dict, List

from app.adaptive_data.models import TrainingReadyDataset
from app.integrations.autoscientist.models import AutoScientistResult
from app.research.models import FailurePattern

logger = logging.getLogger("dataset_genome.research.analyzer")


class ResearchAnalyzer:
    """
    Analyzes experimental benchmark evidence to detect why model performance lagged.
    """

    def analyze_iteration(
        self,
        dataset: TrainingReadyDataset,
        result: AutoScientistResult,
    ) -> List[FailurePattern]:
        """
        Analyze dataset metrics and AutoScientist evaluation results to identify failure patterns.
        """
        failures: List[FailurePattern] = []

        # 1. Model accuracy check
        acc_raw = result.evaluation.hypothesis_accuracy
        acc = acc_raw * 100.0 if acc_raw <= 1.0 else acc_raw
        if acc < 85.0:
            failures.append(
                FailurePattern(
                    category="Hypothesis Accuracy Gap",
                    description=f"Model hypothesis evaluation accuracy ({acc:.1f}%) is below target threshold (85.0%).",
                    severity="HIGH" if acc < 75.0 else "MEDIUM",
                )
            )

        # 2. Reasoning quality check
        reasoning_score = result.evaluation.reasoning_quality_score
        if reasoning_score < 80.0:
            failures.append(
                FailurePattern(
                    category="Hard Reasoning Gap",
                    description=f"Reasoning quality score ({reasoning_score:.1f}/100) indicates insufficient multi-step deduction depth.",
                    severity="HIGH" if reasoning_score < 70.0 else "MEDIUM",
                )
            )

        # 3. Domain distribution check & weak domains
        records = dataset.cleaned_records
        domain_counts: Dict[str, int] = {}
        hard_count = 0
        for r in records:
            d = getattr(r, "domain", "General")
            domain_counts[d] = domain_counts.get(d, 0) + 1
            diff = getattr(r, "difficulty", "medium")
            if str(diff).lower() == "hard":
                hard_count += 1

        total = max(1, len(records))
        for dom, cnt in domain_counts.items():
            pct = (cnt / total) * 100.0
            if pct < 20.0:
                failures.append(
                    FailurePattern(
                        category="Weak Domain Representation",
                        description=f"Domain '{dom}' represents only {pct:.1f}% of total samples ({cnt}/{total}).",
                        severity="MEDIUM",
                        affected_domain=dom,
                    )
                )

        # Explicit check for key scientific domain gaps if missing completely
        key_domains = ["Oncology", "Genetics", "Clinical Trials", "Agriculture"]
        for kd in key_domains:
            if kd not in domain_counts:
                failures.append(
                    FailurePattern(
                        category="Coverage Gap",
                        description=f"Key domain '{kd}' missing from dataset sample representation.",
                        severity="LOW",
                        affected_domain=kd,
                    )
                )

        # 4. Experiment diversity check
        diversity = dataset.adaptive_report.coverage_score
        if diversity < 80.0:
            failures.append(
                FailurePattern(
                    category="Low Experiment Diversity",
                    description=f"Experimental coverage score ({diversity:.1f}) indicates repetitive experiment protocols.",
                    severity="HIGH" if diversity < 60.0 else "MEDIUM",
                )
            )

        # 5. Failure case coverage check
        hard_ratio = (hard_count / total) * 100.0
        if hard_ratio < 25.0:
            failures.append(
                FailurePattern(
                    category="Low Failure Coverage",
                    description=f"Hard/edge-case sample ratio ({hard_ratio:.1f}%) is below 25.0% failure coverage benchmark.",
                    severity="MEDIUM",
                )
            )

        logger.info(f"ResearchAnalyzer identified {len(failures)} failure patterns for analysis.")
        return failures

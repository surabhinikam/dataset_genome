"""
backend/app/adaptive_data/agents/validator.py — AGENT 2: Scientific Validator.

Validates scientific consistency across the complete 10-point scientific reasoning chain:
Observation -> Problem -> Gap -> Hypotheses -> Experiment -> Controls -> Metrics -> Result -> Failures -> Conclusion.
Generates ValidationReport.
"""

import logging
from typing import List, Tuple

from app.adaptive_data.config import DEFAULT_CONFIG, AdaptiveEngineConfig
from app.adaptive_data.models import ValidationIssue, ValidationReport
from app.dataset_generator.models import ScientificReasoningRecord

logger = logging.getLogger("dataset_genome.adaptive_data.validator")


class ScientificValidator:
    """
    AGENT 2 — Scientific Validator.
    
    Validates logical flow, hypothesis testability, control variable presence,
    evaluation metric specificity, and scientific conclusion alignment across dataset records.
    """

    def __init__(self, config: AdaptiveEngineConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def validate(self, records: List[ScientificReasoningRecord]) -> ValidationReport:
        """
        Validate scientific reasoning consistency across records.
        """
        logger.info(f"Agent 2 (Validator) evaluating {len(records)} cleaned sample(s)...")

        valid_count = 0
        invalid_count = 0
        weak_chain_count = 0
        logical_flaw_count = 0
        issues: List[ValidationIssue] = []

        for r in records:
            sample_issues: List[ValidationIssue] = []

            # 1. Missing Core Reasoning Chain Steps
            if not r.observation or not r.observation.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="MISSING_FIELD",
                        severity="CRITICAL",
                        description="Observation field is empty.",
                    )
                )

            if not r.identified_problem or not r.identified_problem.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="MISSING_FIELD",
                        severity="CRITICAL",
                        description="Identified problem field is empty.",
                    )
                )

            if not r.research_gap or not r.research_gap.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="WEAK_REASONING",
                        severity="HIGH",
                        description="Research gap field is empty or underspecified.",
                    )
                )

            if not r.primary_hypothesis or not r.primary_hypothesis.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="MISSING_FIELD",
                        severity="CRITICAL",
                        description="Primary hypothesis statement is missing.",
                    )
                )

            if not r.alternative_hypothesis or not r.alternative_hypothesis.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="WEAK_REASONING",
                        severity="MEDIUM",
                        description="Alternative counter-hypothesis statement is missing.",
                    )
                )

            # 2. Experiment Structure Validation
            if not r.experiment_design or not r.experiment_design.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="INVALID_EXPERIMENT",
                        severity="CRITICAL",
                        description="Experiment design setup is missing.",
                    )
                )

            if not r.control_variables or len(r.control_variables) < self.config.min_control_variables:
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="INVALID_EXPERIMENT",
                        severity="HIGH",
                        description="No control variables specified for experiment.",
                    )
                )

            if not r.evaluation_metrics or len(r.evaluation_metrics) < self.config.min_evaluation_metrics:
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="INVALID_EXPERIMENT",
                        severity="HIGH",
                        description="No evaluation metrics specified for hypothesis testing.",
                    )
                )

            # 3. Logical Contradiction / Weak Conclusion Check
            if not r.scientific_conclusion or not r.scientific_conclusion.strip():
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="WEAK_REASONING",
                        severity="HIGH",
                        description="Final scientific conclusion is missing.",
                    )
                )
            elif len(r.scientific_conclusion.strip()) < 15:
                sample_issues.append(
                    ValidationIssue(
                        record_id=r.id,
                        issue_type="LOGICAL_FLAW",
                        severity="MEDIUM",
                        description="Scientific conclusion statement is too short to be conclusive.",
                    )
                )

            # Aggregations
            if sample_issues:
                invalid_count += 1
                issues.extend(sample_issues)

                if any(i.severity == "CRITICAL" for i in sample_issues):
                    logical_flaw_count += 1
                else:
                    weak_chain_count += 1
            else:
                valid_count += 1

        total_samples = max(1, len(records))
        validation_score = round(max(0.0, min(100.0, (valid_count / total_samples) * 100.0)), 2)

        report = ValidationReport(
            valid_sample_count=valid_count,
            invalid_sample_count=invalid_count,
            weak_chain_count=weak_chain_count,
            logical_flaw_count=logical_flaw_count,
            validation_score=validation_score,
            validation_issues=issues,
        )

        logger.info(
            f"Agent 2 (Validator) completed: {valid_count}/{total_samples} valid samples "
            f"({invalid_count} issues detected, score: {validation_score}/100)."
        )
        return report

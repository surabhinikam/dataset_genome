"""
services/autoscientist/evaluation_validator.py — Evaluation Validator.

Validates baseline & mutated GenomeReport responses and output EvaluationReport objects.
"""

from typing import List
from schemas.intelligence import GenomeReportResponse
from services.autoscientist.evaluation_models import EvaluationReport


class EvaluationValidator:
    """
    Validates evaluation report inputs and outputs.
    """

    @classmethod
    def validate_inputs(
        cls,
        original_report: GenomeReportResponse,
        transformed_report: GenomeReportResponse
    ) -> bool:
        """Validate input report pair."""
        errors: List[str] = []

        if original_report is None or transformed_report is None:
            errors.append("Both original_report and transformed_report must be provided.")
            raise ValueError(f"Evaluation input validation failed: {'; '.join(errors)}")

        if original_report.health_score is None or transformed_report.health_score is None:
            errors.append("Health scores cannot be missing from input genome reports.")
            raise ValueError(f"Evaluation input validation failed: {'; '.join(errors)}")

        return True

    @classmethod
    def validate_report(cls, report: EvaluationReport) -> bool:
        """Validate output EvaluationReport domain object."""
        errors: List[str] = []

        if not report.evaluation_id:
            errors.append("EvaluationReport 'evaluation_id' is required.")

        if not report.experiment_id:
            errors.append("EvaluationReport 'experiment_id' is required.")

        if report.health_score_before < 0.0 or report.health_score_before > 100.0:
            errors.append(f"Invalid health_score_before ({report.health_score_before}). Must be in [0..100].")

        if report.health_score_after < 0.0 or report.health_score_after > 100.0:
            errors.append(f"Invalid health_score_after ({report.health_score_after}). Must be in [0..100].")

        if errors:
            raise ValueError(f"EvaluationReport validation failed: {'; '.join(errors)}")

        return True

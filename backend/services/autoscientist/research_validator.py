"""
services/autoscientist/research_validator.py — Validation Engine for Research Notebooks.

Validates ResearchNotebook instances, notebook entries, and create request DTOs.
"""

from typing import List, Optional
from services.autoscientist.research_models import NotebookCreateRequest, NotebookEntry, ResearchNotebook


class ResearchNotebookValidator:
    """
    Validator for Research Notebook entries and requests.
    """

    @classmethod
    def validate_notebook(cls, notebook: ResearchNotebook) -> None:
        """
        Validate a ResearchNotebook instance.
        
        Raises ValueError if mandatory fields are invalid.
        """
        if not notebook.notebook_id:
            raise ValueError("ResearchNotebook notebook_id cannot be empty.")

        if not notebook.experiment_id:
            raise ValueError("ResearchNotebook experiment_id cannot be empty.")

        if not notebook.title:
            raise ValueError("ResearchNotebook title cannot be empty.")

    @classmethod
    def validate_entry(cls, entry: NotebookEntry) -> None:
        """
        Validate an individual NotebookEntry object.
        """
        if not entry.entry_id:
            raise ValueError("NotebookEntry entry_id cannot be empty.")

        if entry.confidence < 0.0 or entry.confidence > 1.0:
            raise ValueError(f"Invalid entry confidence score '{entry.confidence}'. Must be between 0.0 and 1.0.")

    @classmethod
    def validate_create_request(cls, request: NotebookCreateRequest) -> None:
        """
        Validate NotebookCreateRequest DTO.
        """
        has_artifacts = any([
            request.report,
            request.observation,
            request.ranked_problem,
            request.reasoning_trace,
            request.hypothesis,
            request.plan,
            request.execution_result,
            request.evaluation_report,
            request.dataset_id,
            request.experiment_id,
        ])
        if not has_artifacts:
            raise ValueError("Must provide at least dataset_id, experiment_id, or stage artifact payload to generate a notebook.")

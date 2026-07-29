"""
api/routes/notebook.py — Scientific Research Notebook API Endpoints.

Provides REST API endpoints for compiling automated 8-stage Research Notebooks,
exporting Markdown/JSON reports, and fetching notebooks by experiment ID.
"""

from typing import Optional
from fastapi import APIRouter, Body, HTTPException, status

from services.autoscientist.research_models import NotebookCreateRequest, NotebookResponse, ResearchNotebook
from services.autoscientist.research_notebook import ScientificResearchNotebookEngine

router = APIRouter(prefix="/autoscientist", tags=["autoscientist-notebook"])
notebook_engine = ScientificResearchNotebookEngine()


@router.post(
    "/notebook",
    response_model=NotebookResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Scientific Research Notebook",
    description=(
        "Compiles an 8-stage Scientific Research Notebook recording Observation, Ranking, Reasoning, "
        "Hypothesis, Planning, Execution, Evaluation, and Lessons Learned, returning Markdown, JSON, "
        "and frontend timeline events."
    ),
)
async def generate_research_notebook(
    payload: Optional[NotebookCreateRequest] = Body(None),
) -> NotebookResponse:
    """
    POST /autoscientist/notebook — Compiles 8-stage Research Notebook.
    """
    request = payload or NotebookCreateRequest()

    try:
        notebook = notebook_engine.compile_notebook(request)
        markdown_rep = notebook_engine.export_markdown(notebook)
        json_rep = notebook_engine.export_json(notebook)

        return NotebookResponse(
            notebook_id=notebook.notebook_id,
            experiment_id=notebook.experiment_id,
            notebook=notebook,
            markdown_report=markdown_rep,
            json_report=json_rep,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/notebook/{experiment_id}",
    response_model=ResearchNotebook,
    status_code=status.HTTP_200_OK,
    summary="Get Research Notebook by Experiment ID",
    description="Retrieves a compiled ResearchNotebook object by its experiment_id.",
)
async def get_notebook_by_experiment_id(experiment_id: str) -> ResearchNotebook:
    """
    GET /autoscientist/notebook/{experiment_id} — Returns ResearchNotebook matching experiment_id or 404.
    """
    notebook = notebook_engine.get_notebook_by_experiment_id(experiment_id)
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ResearchNotebook with experiment_id '{experiment_id}' was not found.",
        )
    return notebook

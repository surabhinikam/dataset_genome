"""
api/routes/explain.py — LLM Scientific Narrator API Endpoint.

Provides REST API endpoint for generating grounded scientific explanations across observations,
reasoning traces, hypotheses, experiment plans, evaluation reports, and research notebooks.
"""

from typing import Optional
from fastapi import APIRouter, Body, HTTPException, status

from services.autoscientist.llm_models import ExplainRequest, ExplainResponse
from services.autoscientist.llm_narrator import LLMScientificNarrator

router = APIRouter(prefix="/autoscientist", tags=["autoscientist-explain"])
narrator_engine = LLMScientificNarrator()


@router.post(
    "/explain",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate LLM Scientific Explanation",
    description=(
        "Translates structured scientific pipeline outputs into multi-audience human-readable narratives "
        "(scientific, executive, technical, and business summaries) using Gemini 2.5 Pro with automatic "
        "deterministic fallback."
    ),
)
async def explain_scientific_stage(
    payload: Optional[ExplainRequest] = Body(None),
) -> ExplainResponse:
    """
    POST /autoscientist/explain — Accepts ExplainRequest with target_type and artifact payload.
    """
    request = payload or ExplainRequest()

    # Extract payload data dictionary
    payload_data = {}
    if request.observation:
        payload_data = request.observation.model_dump(mode="json")
    elif request.reasoning_trace:
        payload_data = request.reasoning_trace.model_dump(mode="json")
    elif request.hypothesis:
        payload_data = request.hypothesis.model_dump(mode="json")
    elif request.plan:
        payload_data = request.plan.model_dump(mode="json")
    elif request.evaluation_report:
        payload_data = request.evaluation_report.model_dump(mode="json")
    elif request.notebook:
        payload_data = request.notebook.model_dump(mode="json")
    else:
        payload_data = {"target_type": request.target_type.value, "dataset_id": str(request.dataset_id) if request.dataset_id else None}

    try:
        explanation = narrator_engine.explain(
            target_type=request.target_type,
            payload_data=payload_data,
        )
        return ExplainResponse(
            target_type=request.target_type,
            explanation=explanation,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

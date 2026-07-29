"""
api/routes/health.py — Health-check endpoint.

A simple liveness probe that confirms the API is running and returns the
current version. Useful for load-balancers, Docker health checks, and CI
smoke tests.
"""

from fastapi import APIRouter

from core.config import settings
from schemas.dataset import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the service status and current API version.",
)
async def health_check() -> HealthResponse:
    """Liveness probe — always returns 200 when the service is running."""
    return HealthResponse(status="ok", version=settings.app_version)

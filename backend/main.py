"""
main.py — FastAPI application entry point for Dataset Genome.

Startup sequence:
  1. Create the FastAPI app instance with metadata.
  2. Register CORS middleware (allows the Next.js frontend).
  3. Mount the aggregated API router.

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.config import settings

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Dataset Genome API — Sprint 1 Foundation. "
        "Provides CSV ingestion and structural metadata extraction."
    ),
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
# All API routes are mounted without an extra prefix so that:
#   GET  /health  and  POST /upload  are accessible at root level.
# In future sprints, add versioned prefixes (e.g. /api/v1) as needed.
app.include_router(api_router)

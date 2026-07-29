"""
api/router.py — Central router that aggregates all route modules.

Adding a new feature? Create a new module in api/routes/ and include its
router here. This keeps main.py clean and avoids route duplication.
"""

from fastapi import APIRouter

from api.routes import analyze, evaluate, execute, explain, health, hypothesis, memory, notebook, observe, plan, rank, reason, upload

# Top-level API router
api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(analyze.router)
api_router.include_router(observe.router)
api_router.include_router(rank.router)
api_router.include_router(reason.router)
api_router.include_router(hypothesis.router)
api_router.include_router(plan.router)
api_router.include_router(execute.router)
api_router.include_router(evaluate.router)
api_router.include_router(memory.router)
api_router.include_router(notebook.router)
api_router.include_router(explain.router)




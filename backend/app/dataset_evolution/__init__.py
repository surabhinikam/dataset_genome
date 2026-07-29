"""
backend/app/dataset_evolution — Dataset Evolution Engine for Scientific Reasoning Benchmark.

Analyzes DatasetAnalysisReport quality reports and generates explainable, prioritized EvolutionPlan
specifications for targeted dataset expansion and health score improvement.
"""

from app.dataset_evolution.models import (
    EvolutionIssue,
    EvolutionPlan,
    EvolutionRecommendation,
    EvolutionSeverity,
)
from app.dataset_evolution.planner import EvolutionPlanner
from app.dataset_evolution.recommender import EvolutionRecommender
from app.dataset_evolution.report import export_plan_json, export_plan_markdown

__all__ = [
    "EvolutionPlanner",
    "EvolutionRecommender",
    "EvolutionPlan",
    "EvolutionIssue",
    "EvolutionRecommendation",
    "EvolutionSeverity",
    "export_plan_json",
    "export_plan_markdown",
]

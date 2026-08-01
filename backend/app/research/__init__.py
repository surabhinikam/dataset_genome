"""
backend/app/research — Autonomous Research Workflow for Dataset Genome.

Implements a closed-loop self-improving AI research workflow.
Dataset -> Intelligence -> Evolution -> Adaptive Data -> AutoScientist -> Model Evaluation -> Research Analyzer -> Improvement Plan -> Dataset Evolution -> Next Dataset Version.
"""

from app.research.analyzer import ResearchAnalyzer
from app.research.coordinator import AutonomousResearchCoordinator
from app.research.feedback import ResearchFeedbackEngine
from app.research.models import (
    FailurePattern,
    IterationRecord,
    ResearchImprovementRequest,
    ResearchRecommendation,
    ResearchWorkflowReport,
    StoppingCriteriaConfig,
    VersionLineageRecord,
)
from app.research.planner import ImprovementPlanner
from app.research.report import export_research_report_json, export_research_report_markdown
from app.research.workflow import AutonomousResearchWorkflow

__all__ = [
    "AutonomousResearchCoordinator",
    "AutonomousResearchWorkflow",
    "ResearchAnalyzer",
    "ImprovementPlanner",
    "ResearchFeedbackEngine",
    "ResearchWorkflowReport",
    "IterationRecord",
    "VersionLineageRecord",
    "ResearchImprovementRequest",
    "ResearchRecommendation",
    "StoppingCriteriaConfig",
    "FailurePattern",
    "export_research_report_json",
    "export_research_report_markdown",
]

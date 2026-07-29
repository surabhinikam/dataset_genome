"""
backend/app/orchestrator — Orchestration Engine for Dataset Genome.

Coordinates the end-to-end execution of all platform modules from dataset generation to publication.
Provides single-function execution via DatasetGenomeEngine.run().
"""

from app.orchestrator.config import DEFAULT_ORCHESTRATOR_CONFIG, OrchestratorConfig
from app.orchestrator.engine import DatasetGenomeEngine
from app.orchestrator.events import EventEmitter, GenomeEvent, GenomeEventType
from app.orchestrator.executor import StageExecutor
from app.orchestrator.models import ExecutionReport
from app.orchestrator.pipeline import OrchestratorPipeline
from app.orchestrator.progress import ProgressTracker
from app.orchestrator.report import export_run_report_json, export_run_report_markdown
from app.orchestrator.state_machine import ExecutionState, ExecutionStateMachine

__all__ = [
    "DatasetGenomeEngine",
    "OrchestratorPipeline",
    "ExecutionStateMachine",
    "ExecutionState",
    "EventEmitter",
    "GenomeEvent",
    "GenomeEventType",
    "ProgressTracker",
    "StageExecutor",
    "ExecutionReport",
    "OrchestratorConfig",
    "DEFAULT_ORCHESTRATOR_CONFIG",
    "export_run_report_json",
    "export_run_report_markdown",
]

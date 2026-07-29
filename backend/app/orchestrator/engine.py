"""
backend/app/orchestrator/engine.py — DatasetGenomeEngine Entry Point.

Main entry point for Dataset Genome platform execution.
Calling engine.run() executes all 7 workflow stages automatically.
"""

import logging
from typing import Optional

from app.orchestrator.config import DEFAULT_ORCHESTRATOR_CONFIG, OrchestratorConfig
from app.orchestrator.events import EventEmitter
from app.orchestrator.models import ExecutionReport
from app.orchestrator.pipeline import OrchestratorPipeline

logger = logging.getLogger("dataset_genome.orchestrator.engine")


class DatasetGenomeEngine:
    """
    Dataset Genome Engine — Master Orchestrator.
    
    Provides the single-function execution entry point `run()` that coordinates all platform modules.
    """

    def __init__(
        self,
        config: OrchestratorConfig = DEFAULT_ORCHESTRATOR_CONFIG,
        event_emitter: Optional[EventEmitter] = None,
    ) -> None:
        self.config = config
        self.event_emitter = event_emitter or EventEmitter()
        self.pipeline = OrchestratorPipeline(config=config, event_emitter=self.event_emitter)

    def run(
        self,
        domain: str = "Agriculture",
        count: int = 20,
        dataset_version: str = "v2.0-adaptive",
        model_version: str = "v1.0",
        changes_description: str = "Dataset Genome autonomous end-to-end platform run",
    ) -> ExecutionReport:
        """
        Execute the complete Dataset Genome platform pipeline automatically.
        
        Usage:
            engine = DatasetGenomeEngine()
            report = engine.run(domain="Medicine", count=25)
        """
        logger.info("DatasetGenomeEngine.run() invoked. Initiating autonomous platform pipeline...")
        return self.pipeline.run_pipeline(
            domain=domain,
            count=count,
            dataset_version=dataset_version,
            model_version=model_version,
            changes_description=changes_description,
        )

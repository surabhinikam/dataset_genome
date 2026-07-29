"""
backend/app/orchestrator/pipeline.py — OrchestratorPipeline Coordinator.

Coordinates the 7 sequential stages across existing Dataset Genome modules:
Generator -> Intelligence -> Evolution -> Adaptive Data -> AutoScientist -> Publication -> Notification.
Reuses existing modules without duplicating business logic.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from app.adaptive_data import AdaptiveDataPipeline, TrainingReadyDataset
from app.dataset_evolution import EvolutionPlan, EvolutionPlanner
from app.dataset_generator import DatasetGenerator, ScientificReasoningRecord
from app.dataset_intelligence import DatasetAnalysisReport, DatasetAnalyzer
from app.integrations.autoscientist import AutoScientistAdapter, AutoScientistResult
from app.orchestrator.config import DEFAULT_ORCHESTRATOR_CONFIG, OrchestratorConfig
from app.orchestrator.events import EventEmitter, GenomeEvent, GenomeEventType
from app.orchestrator.executor import StageExecutor
from app.orchestrator.models import ExecutionReport
from app.orchestrator.progress import ProgressTracker
from app.orchestrator.state_machine import ExecutionState, ExecutionStateMachine
from app.publication import PublicationPipeline, PublicationReport

logger = logging.getLogger("dataset_genome.orchestrator.pipeline")


class OrchestratorPipeline:
    """
    Core Orchestrator Pipeline coordinating all 7 stages.
    """

    def __init__(
        self,
        config: OrchestratorConfig = DEFAULT_ORCHESTRATOR_CONFIG,
        event_emitter: Optional[EventEmitter] = None,
    ) -> None:
        self.config = config
        self.event_emitter = event_emitter or EventEmitter()
        self.state_machine = ExecutionStateMachine()
        self.progress_tracker = ProgressTracker()
        self.stage_executor = StageExecutor(max_retries=config.max_stage_retries)

        # Reuse existing modules cleanly (No duplicate business logic)
        self.generator = DatasetGenerator()
        self.analyzer = DatasetAnalyzer()
        self.evolution_planner = EvolutionPlanner()
        self.adaptive_pipeline = AdaptiveDataPipeline()
        self.autoscientist_adapter = AutoScientistAdapter()
        self.publication_pipeline = PublicationPipeline()

    def run_pipeline(
        self,
        domain: str = "Agriculture",
        count: int = 20,
        dataset_version: str = "v2.0-adaptive",
        model_version: str = "v1.0",
        changes_description: str = "Automated full platform orchestration run",
    ) -> ExecutionReport:
        """
        Execute full end-to-end platform workflow.
        """
        execution_id = f"exec-run-{uuid.uuid4().hex[:8]}"
        logger.info(f"OrchestratorPipeline starting run '{execution_id}' (Domain: '{domain}', Count: {count})...")

        self.progress_tracker.start_timer()
        errors: List[str] = []
        warnings: List[str] = []
        artifacts: List[str] = []

        records: List[ScientificReasoningRecord] = []
        intel_report: Optional[DatasetAnalysisReport] = None
        evolution_plan: Optional[EvolutionPlan] = None
        training_ready: Optional[TrainingReadyDataset] = None
        autoscientist_result: Optional[AutoScientistResult] = None
        pub_report: Optional[PublicationReport] = None

        try:
            # STAGE 1: Dataset Generator
            self.state_machine.transition_to(ExecutionState.GENERATING)
            self.progress_tracker.update_stage(ExecutionState.GENERATING, 14.0)

            def stage_1():
                return self.generator.generate(domain=domain, count=count)

            records, _ = self.stage_executor.execute_stage("Dataset Generator", stage_1)
            self.progress_tracker.update_stage(ExecutionState.GENERATING, 14.0, "DatasetGenerator")
            self._emit(GenomeEventType.DatasetGenerated, execution_id, "Dataset Generator", {"sample_count": len(records)})

            # STAGE 2: Dataset Intelligence
            self.state_machine.transition_to(ExecutionState.ANALYZING)
            self.progress_tracker.update_stage(ExecutionState.ANALYZING, 28.0)

            def stage_2():
                return self.analyzer.analyze_records(records)

            intel_report, _ = self.stage_executor.execute_stage("Dataset Intelligence", stage_2)
            self.progress_tracker.update_stage(ExecutionState.ANALYZING, 28.0, "DatasetIntelligence")
            self._emit(GenomeEventType.DatasetAnalyzed, execution_id, "Dataset Intelligence", {"health_score": intel_report.health_scores.overall_dataset_health_score})

            # STAGE 3: Evolution Planner
            self.state_machine.transition_to(ExecutionState.EVOLVING)
            self.progress_tracker.update_stage(ExecutionState.EVOLVING, 42.0)

            def stage_3():
                return self.evolution_planner.create_plan(intel_report)

            evolution_plan, _ = self.stage_executor.execute_stage("Evolution Planner", stage_3)
            self.progress_tracker.update_stage(ExecutionState.EVOLVING, 42.0, "EvolutionPlanner")
            self._emit(GenomeEventType.EvolutionCompleted, execution_id, "Evolution Planner", {"issue_count": len(evolution_plan.issues)})

            # STAGE 4: Adaptive Data Engine
            self.state_machine.transition_to(ExecutionState.OPTIMIZING)
            self.progress_tracker.update_stage(ExecutionState.OPTIMIZING, 57.0)

            def stage_4():
                return self.adaptive_pipeline.process(records=records, intelligence_report=intel_report, dataset_version=dataset_version)

            training_ready, _ = self.stage_executor.execute_stage("Adaptive Data Engine", stage_4)
            self.progress_tracker.update_stage(ExecutionState.OPTIMIZING, 57.0, "AdaptiveDataEngine")
            self._emit(GenomeEventType.AdaptiveCompleted, execution_id, "Adaptive Data Engine", {"adaptive_score": training_ready.adaptive_score})

            # STAGE 5: AutoScientist Adapter
            self.state_machine.transition_to(ExecutionState.TRAINING)
            self.progress_tracker.update_stage(ExecutionState.TRAINING, 71.0)

            def stage_5():
                return self.autoscientist_adapter.execute_integration(training_ready)

            autoscientist_result, _ = self.stage_executor.execute_stage("AutoScientist Adapter", stage_5)
            self.progress_tracker.update_stage(ExecutionState.TRAINING, 71.0, "AutoScientistAdapter")
            self._emit(GenomeEventType.TrainingCompleted, execution_id, "AutoScientist Adapter", {"hypothesis_accuracy": autoscientist_result.evaluation.hypothesis_accuracy})

            # STAGE 6: Publication Engine
            self.state_machine.transition_to(ExecutionState.PUBLISHING)
            self.progress_tracker.update_stage(ExecutionState.PUBLISHING, 85.0)

            def stage_6():
                return self.publication_pipeline.run(
                    dataset=training_ready,
                    autoscientist_result=autoscientist_result,
                    model_version=model_version,
                    changes_description=changes_description,
                )

            pub_report, _ = self.stage_executor.execute_stage("Publication Engine", stage_6)
            artifacts.extend(pub_report.artifacts_generated)
            self.progress_tracker.update_stage(ExecutionState.PUBLISHING, 85.0, "PublicationEngine")
            self._emit(GenomeEventType.PublicationCompleted, execution_id, "Publication Engine", {"artifacts_count": len(pub_report.artifacts_generated)})

            # STAGE 7: Dashboard Notification & Completion
            self.state_machine.transition_to(ExecutionState.COMPLETED)
            self.progress_tracker.update_stage(ExecutionState.COMPLETED, 100.0, "DashboardNotifier")
            self.progress_tracker.stop_timer()

            self._emit(GenomeEventType.PipelineCompleted, execution_id, "Dashboard Notifier", {"total_time": self.progress_tracker.execution_time_seconds})

            return ExecutionReport(
                execution_id=execution_id,
                dataset_version=dataset_version,
                adaptive_score=training_ready.adaptive_score if training_ready else 0.0,
                training_status=autoscientist_result.training_status.value if autoscientist_result else "UNKNOWN",
                publication_status="READY" if pub_report and pub_report.hf_ready else "FAILED",
                execution_time_seconds=self.progress_tracker.execution_time_seconds,
                errors=errors,
                warnings=warnings,
                generated_artifacts=artifacts,
                final_state=ExecutionState.COMPLETED,
            )

        except Exception as exc:
            logger.error(f"OrchestratorPipeline execution failed: {exc}")
            errors.append(str(exc))
            self.state_machine.transition_to(ExecutionState.FAILED)
            self.progress_tracker.stop_timer()
            self._emit(GenomeEventType.PipelineFailed, execution_id, self.state_machine.current_state.value, {"error": str(exc)})

            return ExecutionReport(
                execution_id=execution_id,
                dataset_version=dataset_version,
                adaptive_score=0.0,
                training_status="FAILED",
                publication_status="FAILED",
                execution_time_seconds=self.progress_tracker.execution_time_seconds,
                errors=errors,
                warnings=warnings,
                generated_artifacts=artifacts,
                final_state=ExecutionState.FAILED,
            )

    def _emit(self, event_type: GenomeEventType, execution_id: str, stage_name: str, payload: Dict[str, Any]) -> None:
        if self.config.enable_events:
            evt = GenomeEvent(
                event_type=event_type,
                execution_id=execution_id,
                stage_name=stage_name,
                payload=payload,
            )
            self.event_emitter.emit(evt)

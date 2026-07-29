"""
tests/test_orchestrator.py — Unit & Integration tests for Phase 6 Orchestration Engine.

Tests ExecutionStateMachine, EventEmitter, ProgressTracker, StageExecutor,
DatasetGenomeEngine.run(), and report exporters (run_report.json, run_report.md).
"""

from pathlib import Path
import pytest

from app.orchestrator import (
    DatasetGenomeEngine,
    EventEmitter,
    ExecutionReport,
    ExecutionState,
    ExecutionStateMachine,
    GenomeEvent,
    GenomeEventType,
    OrchestratorConfig,
    ProgressTracker,
    StageExecutor,
    export_run_report_json,
    export_run_report_markdown,
)


def test_execution_state_machine():
    """Test ExecutionStateMachine transition rules."""
    sm = ExecutionStateMachine()
    assert sm.current_state == ExecutionState.INITIALIZED

    sm.transition_to(ExecutionState.GENERATING)
    assert sm.current_state == ExecutionState.GENERATING

    sm.transition_to(ExecutionState.ANALYZING)
    assert sm.current_state == ExecutionState.ANALYZING

    sm.transition_to(ExecutionState.FAILED)
    assert sm.current_state == ExecutionState.FAILED

    # Reset allowed from FAILED
    sm.transition_to(ExecutionState.INITIALIZED)
    assert sm.current_state == ExecutionState.INITIALIZED


def test_event_emitter():
    """Test EventEmitter listener callbacks."""
    emitter = EventEmitter()
    received_events = []

    def listener(evt: GenomeEvent):
        received_events.append(evt)

    emitter.subscribe(listener)

    emitter.emit(
        GenomeEvent(
            event_type=GenomeEventType.DatasetGenerated,
            execution_id="test-exec-1",
            stage_name="Dataset Generator",
            payload={"count": 10},
        )
    )

    assert len(received_events) == 1
    assert received_events[0].event_type == GenomeEventType.DatasetGenerated
    assert received_events[0].stage_name == "Dataset Generator"


def test_progress_tracker():
    """Test ProgressTracker stage updates and timers."""
    tracker = ProgressTracker()
    tracker.start_timer()

    tracker.update_stage(ExecutionState.GENERATING, 14.0, "DatasetGenerator")
    assert tracker.current_stage == ExecutionState.GENERATING
    assert tracker.progress_percentage == 14.0
    assert "DatasetGenerator" in tracker.completed_modules

    tracker.stop_timer()
    assert tracker.execution_time_seconds >= 0.0


def test_stage_executor_success_and_retry():
    """Test StageExecutor retry mechanism."""
    executor = StageExecutor(max_retries=1)

    # Success case
    res, t = executor.execute_stage("Sample Stage", lambda: 42)
    assert res == 42
    assert t >= 0.0

    # Failure case
    def failing_func():
        raise ValueError("Simulated stage error")

    with pytest.raises(RuntimeError) as exc_info:
        executor.execute_stage("Failing Stage", failing_func)

    assert "Failing Stage" in str(exc_info.value)


def test_dataset_genome_engine_full_autonomous_run(tmp_path):
    """Test DatasetGenomeEngine.run() executing complete 7-stage workflow."""
    config = OrchestratorConfig(
        output_report_dir=str(tmp_path / "reports"),
    )
    engine = DatasetGenomeEngine(config=config)

    emitted_events = []

    def event_logger(evt: GenomeEvent):
        emitted_events.append(evt)

    engine.event_emitter.subscribe(event_logger)

    report = engine.run(
        domain="Agriculture",
        count=10,
        dataset_version="v2.0-adaptive",
        model_version="v1.0",
    )

    assert isinstance(report, ExecutionReport)
    assert report.final_state == ExecutionState.COMPLETED
    assert report.adaptive_score > 0.0
    assert report.training_status == "COMPLETED"
    assert report.publication_status == "READY"
    assert len(report.generated_artifacts) > 5
    assert len(emitted_events) >= 6

    # Test Exporters
    json_path = tmp_path / "run_report.json"
    json_str = export_run_report_json(report, output_path=json_path)
    assert "execution_id" in json_str
    assert json_path.exists()

    md_path = tmp_path / "run_report.md"
    md_str = export_run_report_markdown(report, output_path=md_path)
    assert "# Dataset Genome — Autonomous Execution Run Report" in md_str
    assert md_path.exists()

# Orchestration Engine — Dataset Genome Phase 6

The `orchestrator` module implements the **Central Orchestration Engine** for Dataset Genome. It coordinates and manages the execution of all platform modules from initial synthetic telemetry dataset generation to open-source publishing, enabling single-function platform runs via `DatasetGenomeEngine.run()`.

---

## Architecture & Execution Flow

```text
                        ┌────────────────────────┐
                        │  DatasetGenomeEngine   │
                        │       engine.run()     │
                        └───────────┬────────────┘
                                    │
 1. Dataset Generator   ────────────┼────────────► [INITIALIZED -> GENERATING]
 2. Dataset Intelligence ───────────┼────────────► [ANALYZING]
 3. Evolution Planner   ────────────┼────────────► [EVOLVING]
 4. Adaptive Data Engine ───────────┼────────────► [OPTIMIZING]
 5. AutoScientist Adapter ──────────┼────────────► [TRAINING]
 6. Publication Engine  ────────────┼────────────► [PUBLISHING]
 7. Dashboard Notifier  ────────────┴────────────► [COMPLETED / FAILED]
```

---

## Directory Structure

```text
orchestrator/
├── __init__.py        # Package exports (DatasetGenomeEngine, ExecutionReport)
├── engine.py          # User-facing entry point (DatasetGenomeEngine.run())
├── pipeline.py        # Core OrchestratorPipeline coordinating Stages 1-7
├── executor.py        # StageExecutor managing stage retries and exception capture
├── state_machine.py   # ExecutionStateMachine tracking lifecycle states
├── events.py          # EventEmitter and GenomeEvent broadcasting pattern
├── progress.py        # ProgressTracker managing percentage and timer metrics
├── models.py          # Pydantic v2 schemas for ExecutionReport
├── report.py         # Exporters for run_report.json and run_report.md
├── config.py          # Default domain, sample count, and retry parameters
└── README.md          # Architecture & documentation guide
```

---

## Execution Lifecycle States

| ExecutionState | Description | Next Allowed State |
| :--- | :--- | :--- |
| `INITIALIZED` | Pipeline initialized and ready for execution. | `GENERATING`, `FAILED` |
| `GENERATING` | Stage 1: Dataset Generator creating raw reasoning records. | `ANALYZING`, `FAILED` |
| `ANALYZING` | Stage 2: Dataset Intelligence profiling dataset health. | `EVOLVING`, `FAILED` |
| `EVOLVING` | Stage 3: Evolution Planner identifying quality gaps. | `OPTIMIZING`, `FAILED` |
| `OPTIMIZING` | Stage 4: Adaptive Data Engine cleaning, validating, and enriching. | `TRAINING`, `FAILED` |
| `TRAINING` | Stage 5: AutoScientist Adapter benchmarking reasoning quality. | `PUBLISHING`, `FAILED` |
| `PUBLISHING` | Stage 6: Publication Engine bundling Kaggle & Hugging Face repos. | `COMPLETED`, `FAILED` |
| `COMPLETED` | Stage 7: Pipeline execution finished successfully. | None |
| `FAILED` | Pipeline execution halted due to unrecoverable stage error. | `INITIALIZED` (Reset) |

---

## Event System (`EventEmitter`)

Subscribed observers receive real-time `GenomeEvent` payloads during execution:

- `GenomeEventType.DatasetGenerated`
- `GenomeEventType.DatasetAnalyzed`
- `GenomeEventType.EvolutionCompleted`
- `GenomeEventType.AdaptiveCompleted`
- `GenomeEventType.TrainingCompleted`
- `GenomeEventType.PublicationCompleted`
- `GenomeEventType.PipelineCompleted`
- `GenomeEventType.PipelineFailed`

---

## Usage Example

```python
from app.orchestrator import (
    DatasetGenomeEngine,
    export_run_report_markdown,
    export_run_report_json,
)

# 1. Initialize Master Engine
engine = DatasetGenomeEngine()

# 2. Subscribe Optional Listener to Real-Time Events
engine.event_emitter.subscribe(
    lambda evt: print(f"[EVENT] Stage: {evt.stage_name} | Type: {evt.event_type.value}")
)

# 3. Execute Complete Platform Workflow Automatically
report = engine.run(
    domain="Agriculture",
    count=25,
    dataset_version="v2.0-adaptive",
    model_version="v1.0",
)

print("Execution ID:", report.execution_id)
print("Final State:", report.final_state.value)
print("Adaptive Score:", report.adaptive_score)
print("Execution Time:", report.execution_time_seconds, "s")

# 4. Export Run Reports
export_run_report_json(report, output_path="publication/reports/run_report.json")
export_run_report_markdown(report, output_path="publication/reports/run_report.md")
```

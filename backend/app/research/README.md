# Autonomous Research Workflow — Dataset Genome Phase 8

The `research` module implements the **Autonomous Closed-Loop Research Workflow** for Dataset Genome. Rather than executing a single linear pipeline, it transforms Dataset Genome into a self-improving platform that continuously evolves datasets based on experimental model performance and benchmark evidence.

---

## Closed-Loop Architecture

```text
                  ┌──────────────────────────────────────────────┐
                  │    AutonomousResearchCoordinator            │
                  └──────────────────────┬───────────────────────┘
                                         │
 1. Dataset Generation ──────────────────┼────────────────────────┐
 2. Dataset Intelligence ────────────────┼──────────┐             │
 3. Evolution Planner ───────────────────┼──────────┼─── Iterative│ Loop
 4. Adaptive Data Engine ────────────────┼──────────┼─── (v1 -> v2│ -> v3)
 5. AutoScientist Adapter ───────────────┼──────────┼─────────────│
 6. Model Evaluation ────────────────────┼──────────┘             │
                                         ▼                        │
                         ┌──────────────────────────────┐         │
                         │      Research Analyzer       │         │
                         └───────────────┬──────────────┘         │
                                         ▼                        │
                         ┌──────────────────────────────┐         │
                         │     Improvement Planner      │         │
                         └───────────────┬──────────────┘         │
                                         ▼                        │
                         ┌──────────────────────────────┐         │
                         │    Research Feedback Engine  │─────────┘
                         └──────────────────────────────┘
```

---

## Component Architecture

```text
research/
├── __init__.py        # Package exports (AutonomousResearchCoordinator, ResearchWorkflowReport)
├── coordinator.py     # Master coordinator managing multi-iteration research loop
├── workflow.py        # Single-iteration workflow execution engine
├── analyzer.py        # ResearchAnalyzer assessing accuracy, reasoning quality, and failure patterns
├── planner.py         # ImprovementPlanner formulating prioritized evolution recommendations
├── feedback.py        # ResearchFeedbackEngine creating improvement requests and tracking deltas
├── models.py          # Pydantic v2 schemas for IterationRecord and ResearchWorkflowReport
├── report.py         # Report exporters (research_report.json, research_report.md)
└── README.md          # Architecture & documentation guide
```

---

## Configurable Stopping Criteria

The research loop evaluates configurable stopping rules after each iteration:

- `max_iterations`: Maximum loop iterations (default: `3`).
- `target_adaptive_score`: Target adaptive dataset score (default: `85.0`).
- `target_evaluation_score`: Target AutoScientist hypothesis accuracy (default: `90.0`).
- `min_improvement_threshold`: Minimum score delta required to continue loop (default: `0.5`).

---

## Usage Example

```python
from app.research import (
    AutonomousResearchCoordinator,
    StoppingCriteriaConfig,
    export_research_report_json,
    export_research_report_markdown,
)

# 1. Define Custom Stopping Criteria
criteria = StoppingCriteriaConfig(
    max_iterations=3,
    target_adaptive_score=85.0,
    target_evaluation_score=90.0,
)

# 2. Instantiate Master Research Coordinator
coordinator = AutonomousResearchCoordinator(stopping_criteria=criteria)

# 3. Execute Closed-Loop Autonomous Research Workflow
report = coordinator.run_research_loop(
    domain="Agriculture",
    initial_count=20,
)

print("Research Run ID:", report.research_id)
print("Total Iterations:", report.total_iterations)
print("Stopping Reason:", report.stopping_reason)
print(f"Adaptive Score: {report.initial_adaptive_score:.1f} -> {report.final_adaptive_score:.1f} (+{report.score_delta:.2f})")
print(f"Accuracy: {report.initial_accuracy:.1f}% -> {report.final_accuracy:.1f}%")

# 4. Export Research Reports
export_research_report_json(report, output_path="publication/reports/research_report.json")
export_research_report_markdown(report, output_path="publication/reports/research_report.md")
```

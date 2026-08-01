# Benchmark & Evaluation Framework — Dataset Genome Phase 9

The `evaluation` framework evaluates whether Dataset Genome actually improves dataset quality and downstream model performance by providing rigorous, empirical scientific evidence.

---

## Architectural Architecture & Data Flow

```text
                               Raw Dataset
                                    │
                                    ▼
                         ┌────────────────────┐
                         │  Benchmark Runner  │
                         └──────────┬─────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        ┌───────────────────┐               ┌───────────────────┐
        │  Raw Evaluation   │               │ Dataset Genome    │
        │  (Baseline Run)   │               │ Adaptive Engine   │
        └─────────┬─────────┘               └─────────┬─────────┘
                  │                                   │
                  │                         ┌─────────┴─────────┐
                  │                         │  AutoScientist    │
                  │                         │  Model Training   │
                  │                         └─────────┬─────────┘
                  │                                   │
                  ▼                                   ▼
        ┌───────────────────┐               ┌───────────────────┐
        │ Benchmark Run     │               │ Benchmark Run     │
        │ (Raw Dataset)     │               │ (Optimized DS)    │
        └─────────┬─────────┘               └─────────┬─────────┘
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
                         ┌────────────────────┐
                         │ Dataset Comparator │
                         └──────────┬─────────┘
                                    ▼
                         ┌────────────────────┐
                         │Metrics & Leaderboard│
                         └──────────┬─────────┘
                                    ▼
                         ┌────────────────────┐
                         │ Evaluation Report  │
                         └────────────────────┘
```

---

## Evaluation Framework Modules

```text
evaluation/
├── __init__.py        # Package exports (BenchmarkRunner, MetricsEngine, DatasetComparator, etc.)
├── benchmark.py       # MODULE 1: BenchmarkRunner for multi-domain, multi-version experiment runs
├── metrics.py         # MODULE 2: MetricsEngine for computing Dataset Health, Coverage, F1, Accuracy
├── comparator.py      # MODULE 3: DatasetComparator for Raw vs Optimized score deltas & visual charts
├── experiments.py     # MODULE 4: ExperimentTracker for experiment history, timing, & metadata
├── leaderboard.py     # MODULE 5: EvaluationLeaderboard ranking datasets & downstream models
├── report.py          # MODULE 6: Report exporters (evaluation_report.json, evaluation_report.md)
├── models.py          # Pydantic v2 schemas for all evaluation metrics & reports
├── config.py          # EvaluationConfig configuration settings
└── README.md          # Architectural guide & usage documentation
```

---

## Core Metrics

- **Dataset Health Score**: Overall structural health [0..100].
- **Knowledge Coverage Score**: Graph representation & scientific coverage [0..100].
- **Reasoning Quality Score**: Deduction density & multi-step validity [0..100].
- **Experiment Diversity**: Protocol and modality variation [0..100].
- **Adaptive Score**: Adaptive Data Engine composite score [0..100].
- **Downstream Training Accuracy**: AutoScientist hypothesis accuracy [0..100%].
- **F1 Score**: Classification macro F1 score [0..1.0].
- **Precision / Recall**: Precision and recall balance [0..1.0].
- **Inference Success Rate**: Benchmark inference completion rate [0..100%].

---

## Code Usage Example

```python
from app.evaluation import (
    BenchmarkRunner,
    DatasetComparator,
    EvaluationLeaderboard,
    export_evaluation_report_json,
    export_evaluation_report_markdown,
    EvaluationReport,
)

# 1. Run Multi-Domain Benchmark Experiments
runner = BenchmarkRunner()
paired_results = runner.run_multi_domain_benchmark(
    domains=["Agriculture", "Oncology", "Genetics"],
    sample_count_per_domain=20,
)

# 2. Compare Raw vs Optimized Benchmark Runs
comparator = DatasetComparator()
comparisons = []
all_runs = []

for raw_run, opt_run in paired_results:
    comp = comparator.compare_runs(raw_run, opt_run)
    comparisons.append(comp)
    all_runs.extend([raw_run, opt_run])

# 3. Generate Evaluation Leaderboard
leaderboard_engine = EvaluationLeaderboard()
leaderboard_entries = leaderboard_engine.generate_leaderboard(all_runs)

# 4. Construct Full Evaluation Report
report = EvaluationReport(
    eval_id="eval-run-001",
    total_experiments=len(all_runs),
    best_dataset_version=leaderboard_entries[0].dataset_version,
    best_model_version=leaderboard_entries[0].model_version,
    overall_improvement_pct=sum(c.overall_improvement_score for c in comparisons) / len(comparisons),
    comparisons=comparisons,
    leaderboard=leaderboard_entries,
    recommendations=["Deploy optimized v1.0 dataset version to production benchmark training."],
)

# 5. Export Reports (JSON & Markdown with Visual Charts)
export_evaluation_report_json(report, output_path="publication/reports/evaluation_report.json")
export_evaluation_report_markdown(report, output_path="publication/reports/evaluation_report.md")
```

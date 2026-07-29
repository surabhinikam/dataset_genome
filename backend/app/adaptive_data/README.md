# Adaptive Data Engine — Dataset Genome Phase 3

The `adaptive_data` module implements the **Adaptive Data Engine** — the core optimization layer of Dataset Genome that transforms raw/evolved scientific reasoning datasets into scientifically validated, balanced, enriched, and training-ready datasets for AutoScientist.

---

## Architecture Overview

```text
Evolved Dataset (JSONL / ScientificReasoningRecord)
                         │
                         ▼
             ┌───────────────────────┐
             │ AdaptiveDataPipeline  │
             └───────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Agent 1    │  │   Agent 2    │  │   Agent 3    │
│   Cleaner    │  │  Validator   │  │   Balancer   │
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Agent 4    │  │   Agent 5    │  │   Agent 6    │
│  Optimizer   │  │   Enricher   │  │    Scorer    │
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                 │                 │
        └────────────────┼────────────────┘
                         ▼
               TrainingReadyDataset
```

---

## Directory Structure

```text
adaptive_data/
│
├── __init__.py      # Package exports (AdaptiveDataPipeline, TrainingReadyDataset)
├── pipeline.py      # Core AdaptiveDataPipeline coordinator orchestrating Agents 1-6
├── models.py        # Pydantic v2 schemas for reports and TrainingReadyDataset
├── report.py       # JSON, Markdown, and JSONL training dataset exporters
├── config.py        # Quality thresholds and agent scoring weights
│
├── agents/
│   ├── cleaner.py   # Agent 1: Dataset Cleaner (duplicates, corrupted, empty fields)
│   ├── validator.py # Agent 2: Scientific Validator (10-point reasoning chain consistency)
│   ├── balancer.py  # Agent 3: Dataset Balancer (domain, difficulty & experiment parity)
│   ├── optimizer.py # Agent 4: Dataset Optimizer (translates intelligence profiling to plans)
│   ├── enricher.py  # Agent 5: Dataset Enricher (context, alternative hypotheses, metrics)
│   └── scorer.py    # Agent 6: Adaptive Scorer (composite score & training readiness)
│
└── README.md        # Architecture & documentation guide
```

---

## Autonomous Agent Specifications

| Agent | Module | Core Responsibilities | Generated Report |
| :--- | :--- | :--- | :--- |
| **Agent 1: Cleaner** | `agents/cleaner.py` | Removes duplicate IDs/prompts, invalid samples, corrupted entries, and malformed strings. | `CleaningReport` |
| **Agent 2: Validator** | `agents/validator.py` | Validates complete 10-step scientific reasoning chain (Observation $\rightarrow$ Problem $\rightarrow$ Gap $\rightarrow$ Hypotheses $\rightarrow$ Experiment $\rightarrow$ Controls $\rightarrow$ Metrics $\rightarrow$ Result $\rightarrow$ Failures $\rightarrow$ Conclusion). | `ValidationReport` |
| **Agent 3: Balancer** | `agents/balancer.py` | Analyzes distributions across domains, difficulty, and experiment types; detects domain starvation. | `BalanceReport` |
| **Agent 4: Optimizer** | `agents/optimizer.py` | Translates `DatasetAnalysisReport` metrics into prioritized optimization plans. | `OptimizationPlan` |
| **Agent 5: Enricher** | `agents/enricher.py` | Refines scientific context, strengthens alternative hypotheses, adds evaluation metrics. | `EnrichmentReport` |
| **Agent 6: Scorer** | `agents/scorer.py` | Synthesizes agent sub-scores into `overall_adaptive_score` and determines `training_readiness`. | `AdaptiveDataReport` |

---

## Usage Example

```python
from app.dataset_generator import DatasetGenerator
from app.dataset_intelligence import DatasetAnalyzer
from app.adaptive_data import (
    AdaptiveDataPipeline,
    export_adaptive_report_markdown,
    export_training_jsonl,
)

# 1. Generate Baseline Dataset Records
generator = DatasetGenerator()
records = generator.generate("Agriculture", 20)

# 2. Run Dataset Intelligence Profiling
analyzer = DatasetAnalyzer()
intel_report = analyzer.analyze_records(records)

# 3. Execute Adaptive Data Engine Pipeline
pipeline = AdaptiveDataPipeline()
training_ready = pipeline.process(records, intelligence_report=intel_report)

print("Composite Adaptive Score:", training_ready.adaptive_score)
print("Training Readiness:", training_ready.training_ready)

# 4. Export Reports & Training-Ready JSONL Dataset
export_adaptive_report_markdown(training_ready, output_path="datasets/metadata/adaptive_report.md")
export_training_jsonl(training_ready, output_path="datasets/final/train.jsonl")
```

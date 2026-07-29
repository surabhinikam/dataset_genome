# AutoScientist Integration Layer — Dataset Genome Phase 4

The `integrations/autoscientist` module implements the **AutoScientist Integration Layer** for Dataset Genome. It acts as an extensible, modular bridge between Dataset Genome's optimized training datasets (`TrainingReadyDataset`) and the AutoScientist execution & reasoning engines.

---

## Architecture Overview

```text
TrainingReadyDataset (From Phase 3 Adaptive Data Engine)
                         │
                         ▼
             ┌───────────────────────┐
             │ AutoScientistAdapter  │
             └───────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Module 1   │  │   Module 2   │  │   Module 3   │
│Dataset Mapper│  │Client Bridge │  │  Evaluator   │
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                 │                 │
        └────────────────┼────────────────┘
                         ▼
                  ┌──────────────┐
                  │   Module 4   │
                  │Feedback Engine│
                  └───────┬──────┘
                          ▼
                AutoScientistResult
```

---

## Directory Structure

```text
autoscientist/
├── __init__.py      # Package exports
├── adapter.py      # Core AutoScientistAdapter coordinator
├── client.py       # Module 2: Client abstraction (BaseAutoScientistClient, MockAutoScientistClient)
├── mapper.py       # Module 1: Dataset Mapper (converts TrainingReadyDataset -> MappedDataset)
├── evaluator.py    # Module 3: Experiment Evaluator (parses benchmark metrics & reasoning quality)
├── feedback.py     # Module 4: Feedback Engine (translates model weaknesses -> dataset actions)
├── models.py       # Pydantic v2 schemas for MappedDataset, AutoScientistResult, etc.
├── report.py       # JSON and Markdown report exporters
├── config.py       # AutoScientist API URLs and evaluation thresholds
└── README.md        # Architecture & documentation guide
```

---

## The Four Core Integration Modules

| Module | File | Responsibilities | Output Model |
| :--- | :--- | :--- | :--- |
| **Module 1: Mapper** | `mapper.py` | Converts `TrainingReadyDataset` into standardized `MappedDataset` payload with 10-point reasoning chains. | `MappedDataset` |
| **Module 2: Client** | `client.py` | Abstract client interface (`BaseAutoScientistClient`) providing `prepare()`, `submit()`, `monitor()`, and `collect_results()`. | `Dict[str, Any]` (Raw Results) |
| **Module 3: Evaluator** | `evaluator.py` | Parses execution outputs; extracts hypothesis accuracy, reasoning quality, confidence scores, and domain metrics. | `ExperimentEvaluationReport` |
| **Module 4: Feedback** | `feedback.py` | Translates model performance weaknesses back into Dataset Genome dataset enhancement recommendations. | `DatasetFeedbackReport` |

---

## Usage Example

```python
from app.dataset_generator import DatasetGenerator
from app.adaptive_data import AdaptiveDataPipeline
from app.integrations.autoscientist import (
    AutoScientistAdapter,
    export_autoscientist_result_markdown,
)

# 1. Generate & Optimize Dataset
generator = DatasetGenerator()
records = generator.generate("Agriculture", 20)

pipeline = AdaptiveDataPipeline()
training_ready = pipeline.process(records)

# 2. Execute AutoScientist Integration Workflow
adapter = AutoScientistAdapter()
result = adapter.execute_integration(training_ready)

print("Job ID:", result.job_id)
print("Hypothesis Accuracy:", result.evaluation.hypothesis_accuracy)
print("Recommended Actions:", result.recommended_dataset_actions)

# 3. Export Markdown Integration & Evaluation Report
export_autoscientist_result_markdown(result, output_path="datasets/metadata/autoscientist_result.md")
```

# Hugging Face Integration Platform — Dataset Genome Phase 5

The `integrations/huggingface` module implements the **Hugging Face Integration Platform** for Dataset Genome. It acts as the publication, versioning, metadata tracking, and distribution preparation layer for Dataset Genome outputs.

---

## Architecture Overview

```text
TrainingReadyDataset & Trained Model Checkpoints
                         │
                         ▼
             ┌───────────────────────┐
             │  HuggingFaceUploader  │
             └───────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Module 1   │  │   Module 2   │  │ Modules 3&4  │
│Dataset Publish│ │ Model Publish│  │Card Generators│
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Module 5   │  │   Module 6   │  │   Module 7   │
│Version Manager│ │Metadata Manage│ │  Client/Upload│
└───────┬──────┘  └───────┬──────┘  └───────┬──────┘
        │                 │                 │
        └────────────────┼────────────────┘
                         ▼
                  PublishingReport
```

---

## Directory Structure

```text
huggingface/
├── __init__.py      # Package exports
├── uploader.py     # Module 7: Core HuggingFaceUploader coordinator
├── client.py       # Module 7: Client abstraction (BaseHuggingFaceClient, MockHuggingFaceClient)
├── dataset.py      # Module 1: Dataset Publisher (bundles dataset files & card)
├── model.py        # Module 2: Model Publisher (bundles checkpoints & model card)
├── cards.py        # Modules 3 & 4: Dataset & Model Card Generators (README.md)
├── versioning.py   # Module 5: Version Manager (v1.0 -> v2.0 -> v3.0 lineage tracking)
├── metadata.py     # Module 6: Metadata Manager (UUID & manifest generation)
├── models.py       # Pydantic v2 schemas for packages & PublishingReport
├── report.py       # JSON and Markdown report exporters
├── config.py       # Organization ID, repo names, and license defaults
└── README.md        # Architecture & documentation guide
```

---

## The Seven Core Integration Modules

| Module | File | Responsibilities | Output Model |
| :--- | :--- | :--- | :--- |
| **Module 1: Dataset Publisher** | `dataset.py` | Bundles training/test dataset files and attached dataset card documentation. | `DatasetPackage` |
| **Module 2: Model Publisher** | `model.py` | Bundles model checkpoints, architecture specs, evaluation metrics, and model card. | `ModelArtifactPackage` |
| **Module 3: Dataset Card Gen** | `cards.py` | Automatically generates Hugging Face Dataset Card `README.md` with statistics, license, and citation. | `str` (Markdown) |
| **Module 4: Model Card Gen** | `cards.py` | Automatically generates Hugging Face Model Card `README.md` with evaluation metrics and intended use. | `str` (Markdown) |
| **Module 5: Version Manager** | `versioning.py` | Tracks semantic dataset release history (`v1.0`, `v2.0`, `v3.0`), changelogs, and scores. | `DatasetVersionRecord` |
| **Module 6: Metadata Manager** | `metadata.py` | Generates Dataset UUID, Model UUID, pipeline manifests, and author attributions. | `GenomeMetadata` |
| **Module 7: Uploader** | `uploader.py` | Provides `prepare()`, `validate()`, `publish_dataset()`, and `publish_model()` orchestrator. | `PublishingReport` |

---

## Usage Example

```python
from app.dataset_generator import DatasetGenerator
from app.adaptive_data import AdaptiveDataPipeline
from app.integrations.huggingface import (
    HuggingFaceUploader,
    export_publishing_report_markdown,
)

# 1. Generate & Optimize Dataset
generator = DatasetGenerator()
records = generator.generate("Agriculture", 20)

pipeline = AdaptiveDataPipeline()
training_ready = pipeline.process(records)

# 2. Execute Hugging Face Publication Pipeline
uploader = HuggingFaceUploader()
report = uploader.publish(
    dataset=training_ready,
    model_version="v1.0",
    changes_description="Dataset Genome v2.0-adaptive publication release",
)

print("Publication ID:", report.publication_id)
print("Ready for Publication:", report.ready_for_publish)
print("Artifact Repos:", report.artifacts)

# 3. Export Markdown Publishing Report
export_publishing_report_markdown(report, output_path="datasets/metadata/publishing_report.md")
```

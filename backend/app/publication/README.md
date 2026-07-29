# Publication & Open Source Engine — Dataset Genome Phase 5

The `publication` module implements the **Publication & Open Source Engine** for Dataset Genome. It transforms optimized dataset records and AutoScientist execution benchmarks into public-ready, open-source research packages for Hugging Face Hub, Kaggle, and Adaption Labs submission releases.

---

## Architecture Overview

```text
TrainingReadyDataset & AutoScientistResult
                         │
                         ▼
             ┌───────────────────────┐
             │  PublicationPipeline  │
             └───────────┬───────────┘
                         │
  ┌──────────────────────┼──────────────────────┐
  ▼                      ▼                      ▼
publication/dataset/   publication/model/     publication/kaggle/
  dataset_final.json     model_metadata.json    dataset-metadata.json
  dataset_stats.json     training_summary.md    README.md
  schema.json            evaluation.json        sample_examples
  metadata.json          weights_manifest.json  statistics
  dataset_summary.md
  │                      │                      │
  └──────────────────────┼──────────────────────┘
                         ▼
  ┌──────────────────────┼──────────────────────┐
  ▼                      ▼                      ▼
publication/huggingface/ publication/reports/  publication/release/
  README.md              publication_report.json CHANGELOG.md
  train.jsonl            publication_report.md
  dataset_info.json
  LICENSE
  MODEL_CARD.md
  DATASET_CARD.md
  config.json
```

---

## Directory Structure

```text
publication/
├── __init__.py      # Package exports (PublicationPipeline, PublicationReport)
├── pipeline.py      # Core PublicationPipeline coordinator executing Modules 1-8
├── models.py        # Pydantic v2 schemas for all publication packages
├── report.py       # JSON and Markdown report exporters
├── config.py        # Target directory paths & license defaults
│
├── artifacts/
│   ├── dataset_packager.py  # Module 1: Dataset Packager (dataset_final.json, schema, etc.)
│   ├── model_packager.py    # Module 2: Model Packager (metadata, evaluation, weights)
│   └── report_packager.py   # Module 8: Report Packager (assembles PublicationReport)
│
├── huggingface/
│   ├── card_generator.py    # Modules 3 & 4: Dataset & Model Card Generators (README.md)
│   ├── dataset.py           # Hugging Face dataset folder bundler
│   ├── model.py             # Hugging Face model repo bundler
│   ├── metadata.py          # Hugging Face dataset_info.json generator
│   ├── validator.py         # Hugging Face package validator
│   └── uploader.py          # Module 7: Hugging Face Package coordinator
│
├── kaggle/
│   ├── metadata.py          # Kaggle CLI dataset-metadata.json generator
│   ├── package.py           # Kaggle sample dataset copy helper
│   ├── validator.py         # Kaggle package validator
│   └── uploader.py          # Module 6: Kaggle Package coordinator
│
├── versioning/
│   ├── dataset_version.py   # Module 5: Dataset version manager (v1.0, v2.0, etc.)
│   ├── model_version.py     # Module 5: Model version manager
│   └── changelog.py         # Module 5: CHANGELOG.md generator
│
└── README.md        # Architecture & documentation guide
```

---

## The Eight Core Publication Modules

| Module | Location | Primary Output Artifacts | Target Directory |
| :--- | :--- | :--- | :--- |
| **Module 1: Dataset Packager** | `artifacts/dataset_packager.py` | `dataset_final.json`, `dataset_statistics.json`, `schema.json`, `metadata.json`, `dataset_summary.md` | `publication/dataset/` |
| **Module 2: Model Packager** | `artifacts/model_packager.py` | `model_metadata.json`, `training_summary.md`, `evaluation.json`, `weights_manifest.json` | `publication/model/` |
| **Module 3: Dataset Card Gen** | `huggingface/card_generator.py` | `README.md` (Dataset Card with statistics, license, BibTeX citation) | `publication/huggingface/` |
| **Module 4: Model Card Gen** | `huggingface/card_generator.py` | `MODEL_CARD.md` (Model Card with architecture and benchmark evaluation) | `publication/huggingface/` |
| **Module 5: Version Manager** | `versioning/` | `CHANGELOG.md` (Version history tracking release tags and scores) | `publication/release/` |
| **Module 6: Kaggle Package** | `kaggle/uploader.py` | `dataset-metadata.json`, `README.md`, `license`, `sample_examples`, `statistics` | `publication/kaggle/` |
| **Module 7: Hugging Face Package** | `huggingface/uploader.py` | `README.md`, `train.jsonl`, `dataset_info.json`, `LICENSE`, `MODEL_CARD.md`, `config.json` | `publication/huggingface/` |
| **Module 8: Publication Report** | `artifacts/report_packager.py` | `publication_report.json`, `publication_report.md` | `publication/reports/` |

---

## Usage Example

```python
from app.dataset_generator import DatasetGenerator
from app.adaptive_data import AdaptiveDataPipeline
from app.integrations.autoscientist import AutoScientistAdapter
from app.publication import PublicationPipeline, export_publication_report_markdown

# 1. Pipeline Execution
generator = DatasetGenerator()
records = generator.generate("Agriculture", 20)

adaptive_pipeline = AdaptiveDataPipeline()
training_ready = adaptive_pipeline.process(records)

adapter = AutoScientistAdapter()
result = adapter.execute_integration(training_ready)

# 2. Generate Master Publication Artifacts
pub_pipeline = PublicationPipeline()
report = pub_pipeline.run(
    dataset=training_ready,
    autoscientist_result=result,
    model_version="v1.0",
    changes_description="Official Adaption Labs Hackathon open-source benchmark submission release",
)

print("Publication ID:", report.publication_id)
print("Kaggle Ready:", report.kaggle_ready)
print("Hugging Face Ready:", report.hf_ready)
print("Total Artifacts:", len(report.artifacts_generated))

# 3. Export Markdown Publication Report
export_publication_report_markdown(report, output_path="publication/reports/publication_report.md")
```

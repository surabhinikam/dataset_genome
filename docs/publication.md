# Publication Pipeline — HuggingFace & Kaggle

## Overview

Dataset Genome includes a complete publication pipeline that packages, validates, and uploads the generated dataset and model to **HuggingFace Hub** and **Kaggle**.

All publication artifacts live in `publication/`.

---

## Directory Structure

```
publication/
├── huggingface/        # HuggingFace dataset package (upload-ready)
│   ├── README.md       # Dataset card (YAML front-matter + content)
│   ├── DATASET_CARD.md # Extended dataset documentation
│   ├── MODEL_CARD.md   # AutoScientist model card
│   ├── LICENSE         # MIT License
│   ├── dataset_info.json  # HF-spec metadata (features, splits, sizes)
│   ├── config.json     # HF dataset config
│   ├── train.jsonl     # Training split (20 Agriculture records, v1.0)
│   └── RELEASE_REPORT.md  # Release verification checklist
│
├── kaggle/             # Kaggle dataset package
│   └── ...
│
├── model/              # Model publication artifacts
│   └── ...
│
├── dataset/            # Dataset release archives
│   └── ...
│
├── release/            # Release tags and manifests
│   └── ...
│
└── reports/            # Publication reports
    └── ...
```

---

## HuggingFace Publication

### Prerequisites

```bash
pip install huggingface-hub
huggingface-cli login   # Requires HF account token
```

### Upload Dataset

```bash
huggingface-cli upload YOUR-HF-USERNAME/dataset-genome-agriculture-mechanism-outcomes \
    publication/huggingface/ \
    --repo-type dataset
```

### Upload Model

```bash
huggingface-cli upload YOUR-HF-USERNAME/autoscientist-reasoning-model \
    publication/model/ \
    --repo-type model
```

### Dataset Card (README.md) Format

The dataset card uses HuggingFace YAML front-matter:

```yaml
---
language:
- en
license:
- mit
tags:
- dataset-genome
- autoscientist
- scientific-reasoning
- agriculture
- benchmark
- hackindia
- adaption-adaptive-data
pretty_name: Dataset Genome - Agriculture Mechanism Outcomes
---
```

### dataset_info.json Specification

The `dataset_info.json` follows the HuggingFace `DatasetInfo` spec:

```json
{
  "name": "dataset-genome-agriculture-mechanism-outcomes",
  "pretty_name": "Dataset Genome - Agriculture Mechanism Outcomes",
  "description": "...",
  "license": "mit",
  "language": ["en"],
  "task_categories": ["text-generation", "question-answering"],
  "task_ids": ["scientific-reasoning", "instruction-following"],
  "size_categories": ["n<1K"],
  "splits": {
    "train": {
      "name": "train",
      "num_bytes": 31902,
      "num_examples": 20
    }
  }
}
```

---

## Release Verification Checklist

Before uploading, verify:

```bash
# Run from publication/huggingface/
ls -la
# Expected: README.md, LICENSE, train.jsonl, dataset_info.json, DATASET_CARD.md, MODEL_CARD.md, config.json
```

| Check | Command | Expected |
|-------|---------|---------|
| train.jsonl exists | `ls train.jsonl` | File present |
| train.jsonl non-empty | `wc -l train.jsonl` | 20 lines |
| No .env | `ls .env` | Not found |
| No API keys | `grep -r "sk-" .` | No matches |
| No safetensors | `find . -name "*.safetensors"` | No matches |
| License consistent | `head -3 LICENSE` | MIT |

Full verification report: [`publication/huggingface/RELEASE_REPORT.md`](../publication/huggingface/RELEASE_REPORT.md)

---

## Kaggle Publication

### Prerequisites

```bash
pip install kaggle
# Configure ~/.kaggle/kaggle.json with your API credentials
```

### Create Dataset

```bash
kaggle datasets create \
    -p publication/kaggle/ \
    --dir-mode zip
```

### Update Existing Dataset

```bash
kaggle datasets version \
    -p publication/kaggle/ \
    -m "v1.0.0 — HackIndia 2026 AutoScientist Challenge release"
```

---

## Automated Publication Pipeline

The backend publication pipeline (`backend/app/publication/`) automates multi-format export:

```python
from app.pipeline.master_orchestrator import DatasetGenomeMasterPipeline

pipeline = DatasetGenomeMasterPipeline(export_dir=export_dir)
samples, report, manifest = await pipeline.execute_pipeline(
    samples_per_domain=1,
    version_tag="v1.0",
    provider_type=None,   # Uses DEFAULT_LLM_PROVIDER from .env
)
```

This single call produces all exports in `export_benchmark/`:
- `benchmark_v1.0.jsonl` — training format
- `benchmark_v1.0.json` — structured archive
- `benchmark_v1.0.csv` — tabular
- `benchmark_v1.0.parquet` — columnar
- `benchmark_v1.0_hf.json` — HuggingFace-ready
- `benchmark_report.json` — quality report
- `reproducibility_manifest.json` — git hash, seeds, provider info

---

## Environment Variables

All publication credentials are managed via `.env`:

```bash
# .env (copy from .env.example)
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.0-flash
```

HuggingFace and Kaggle credentials are managed via their respective CLI tools and are never stored in `.env`.

---

*See [`dataset.md`](dataset.md) for dataset schema and [`benchmark.md`](benchmark.md) for quality metrics.*

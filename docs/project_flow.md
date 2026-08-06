# End-to-End Project Flow

## Overview

This document traces the complete Dataset Genome pipeline from initialization to published artifacts, with detailed Mermaid diagrams at each stage.

---

## High-Level Flow

```mermaid
flowchart TD
    A[🌱 Raw Scientific Scenario Seeds] --> B[Adaptive Data Engine]
    B --> C[LLM Orchestration\nGemini / OpenAI / Anthropic]
    C --> D[Dataset Genome Pipeline\n11-Stage Master Orchestrator]
    D --> E[Validation & Quality Scoring]
    E --> F{Score ≥ Threshold?}
    F -- Yes --> G[Training Dataset\n200 samples, 10 domains]
    F -- No --> H[Retry with Temperature Nudge]
    H --> C
    G --> I[AutoScientist Training\nLoRA + PEFT]
    I --> J[Fine-tuned Model]
    G --> K[Multi-Format Export]
    K --> L[HuggingFace Dataset]
    K --> M[Kaggle Dataset]
    J --> N[HuggingFace Model]
```

---

## Stage 1: LLM Provider Initialization

```mermaid
flowchart LR
    A[.env Config] --> B[LLMConfig]
    B --> C[LLMFactory]
    C --> D{Provider?}
    D -- gemini --> E[GeminiProvider\ngoogle-genai SDK]
    D -- openai --> F[OpenAIProvider\nopenai SDK + tenacity]
    D -- anthropic --> G[AnthropicProvider]
    D -- ollama --> H[OllamaProvider\nlocal]
    E --> I[BaseLLMProvider Interface]
    F --> I
    G --> I
    H --> I
```

**Key files:**
- [`backend/app/llm/config.py`](../backend/app/llm/config.py) — reads `GOOGLE_API_KEY`, `OPENAI_API_KEY` from env
- [`backend/app/llm/factory.py`](../backend/app/llm/factory.py) — `LLMFactory.get_provider()`
- [`backend/app/llm/providers/`](../backend/app/llm/providers/) — concrete implementations

---

## Stage 2: Benchmark Prompt Construction

```mermaid
flowchart LR
    A[domain + difficulty\n+ reasoning_style] --> B[BenchmarkPromptBuilder]
    B --> C[System Message\nScientific Reasoning Expert]
    B --> D[User Message\nStructured JSON Prompt]
    C --> E[LLMRequest]
    D --> E
    E --> F[LLMProvider.generate]
```

**Key files:**
- [`backend/app/benchmark/prompt_builder.py`](../backend/app/benchmark/prompt_builder.py)
- [`backend/app/llm/models.py`](../backend/app/llm/models.py) — `LLMRequest`

---

## Stage 3: Sample Generation with Retry Logic

```mermaid
flowchart TD
    A[LLMBenchmarkGenerator.generate_sample] --> B[Attempt 1\ntemp=0.85]
    B --> C{Parse Success?}
    C -- Yes --> D[BenchmarkQualityScorer\nAttach scores]
    C -- No --> E[Attempt 2\ntemp=0.90]
    E --> F{Parse Success?}
    F -- Yes --> D
    F -- No --> G[Attempt 3\ntemp=0.95]
    G --> H{Parse Success?}
    H -- Yes --> D
    H -- No --> I[GenerationExhaustedError\nSkip slot]
    D --> J[BenchmarkDeduplicator\nCheck duplicate]
    J --> K{Duplicate?}
    K -- No --> L[✅ Sample accepted]
    K -- Yes --> M[Retry with offset index]
```

**Key files:**
- [`backend/app/benchmark/llm_generator.py`](../backend/app/benchmark/llm_generator.py)
- [`backend/app/benchmark/response_parser.py`](../backend/app/benchmark/response_parser.py)
- [`backend/app/benchmark/quality_scorer.py`](../backend/app/benchmark/quality_scorer.py)
- [`backend/app/benchmark/deduplicator.py`](../backend/app/benchmark/deduplicator.py)

---

## Stage 4: Suite Validation

```mermaid
flowchart LR
    A[200 BenchmarkSamples] --> B[BenchmarkValidator]
    B --> C[Field Completeness Check]
    B --> D[Domain Balance Check\n±5% tolerance]
    B --> E[Difficulty Balance Check\n±5% tolerance]
    B --> F[Duplicate Count Check]
    B --> G[Reasoning Chain Check]
    C --> H{All Pass?}
    D --> H
    E --> H
    F --> H
    G --> H
    H -- Yes --> I[✅ Validated Suite]
    H -- No --> J[⚠️ Validation Issues Logged]
    J --> I
```

**Key files:**
- [`backend/app/benchmark/validator.py`](../backend/app/benchmark/validator.py)

---

## Stage 5: 11-Stage Master Orchestrator

The `DatasetGenomeMasterPipeline` orchestrates all stages:

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Initialization | Pipeline config, export dir setup |
| 2 | LLM Provider | Factory instantiation, API key validation |
| 3 | Dataset Generation | Benchmark sample generation across all domains |
| 4 | Validation | Suite validation (domain/difficulty balance, dedup) |
| 5 | Quality Scoring | Composite adaptive score calculation |
| 6 | JSON Export | Structured JSON archive |
| 7 | JSONL Export | Training-format JSONL |
| 8 | CSV Export | Tabular CSV |
| 9 | Parquet Export | Columnar Parquet (via pyarrow) |
| 10 | HuggingFace Export | HF-ready JSON + dataset card |
| 11 | Reporting | Benchmark report, diversity report, leaderboard, manifest |

**Key files:**
- [`backend/app/pipeline/master_orchestrator.py`](../backend/app/pipeline/master_orchestrator.py)

---

## Stage 6: Publication

```mermaid
flowchart TD
    A[benchmark_v1.0.jsonl] --> B[publication/huggingface/]
    B --> C[train.jsonl\n20 Agriculture records]
    B --> D[dataset_info.json\nHF-spec metadata]
    B --> E[README.md\nDataset Card]
    C --> F[huggingface-cli upload]
    D --> F
    E --> F
    F --> G[🤗 HuggingFace Dataset Hub]

    A --> H[publication/kaggle/]
    H --> I[kaggle datasets create]
    I --> J[📊 Kaggle Hub]

    K[LoRA Adapter Weights] --> L[publication/model/]
    L --> M[huggingface-cli upload --repo-type model]
    M --> N[🤗 HuggingFace Model Hub]
```

---

## Running the Full Pipeline

```bash
# 1. Clone and configure
git clone <repo-url>
cd dataset_genome
cp .env.example .env
# Fill in GOOGLE_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run demo (full 11-stage pipeline)
python demo.py

# 4. Review outputs
ls export_benchmark/
# benchmark_v1.0.jsonl, benchmark_report.md, reproducibility_manifest.json, ...
```

---

## Output Artifacts

After running `demo.py`:

| Artifact | Location | Description |
|----------|----------|-------------|
| Full benchmark | `export_benchmark/benchmark_v1.0.jsonl` | 200 samples, JSONL |
| Quality report | `export_benchmark/benchmark_report.json` | Adaptive score, coverage metrics |
| Reproducibility manifest | `export_benchmark/reproducibility_manifest.json` | Git hash, seed, provider |
| Leaderboard | `export_benchmark/benchmark_leaderboard.json` | Version ranking |
| Diversity report | `export_benchmark/dataset_diversity_report.json` | Lexical diversity metrics |
| Dashboard data | `export_benchmark/live_pipeline_status.json` | Frontend analytics |
| HF package | `publication/huggingface/` | Ready to upload |

---

*See [`architecture.md`](architecture.md) for system architecture, [`benchmark.md`](benchmark.md) for quality metrics, and [`publication.md`](publication.md) for upload instructions.*

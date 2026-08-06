# System Architecture — Dataset Genome

## Overview

Dataset Genome is a **full-stack AI research platform** built as a monorepo containing:

1. **Python Backend** — FastAPI REST API + complete ML pipeline
2. **Next.js Frontend** — Real-time benchmark dashboard
3. **Adaptive Data Engine** — Autonomous dataset generation pipeline
4. **Publication Pipeline** — HuggingFace + Kaggle automated publishing

The system is designed for modularity: each subsystem can be used independently, and the complete pipeline runs end-to-end via `demo.py`.

---

## Full System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Next.js 15 Dashboard (localhost:3000)                       │    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐   │    │
│  │  │  Upload UI   │  │  Benchmark View │  │  Pipeline    │   │    │
│  │  │  Component   │  │  Component      │  │  Status      │   │    │
│  │  └──────┬───────┘  └────────┬────────┘  └──────┬───────┘   │    │
│  │         └─────────────────lib/api.ts────────────┘           │    │
│  └────────────────────────────┬────────────────────────────────┘    │
└───────────────────────────────│──────────────────────────────────────┘
                                │ HTTP REST (JSON)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        API LAYER                                     │
│                                                                      │
│  FastAPI Application (localhost:8000)                                │
│                                                                      │
│  ┌──────────┐  ┌─────────────────┐  ┌──────────────────────────┐   │
│  │ GET      │  │ POST /upload    │  │  CORS Middleware          │   │
│  │ /health  │  │ (CSV ingestion) │  │  (Next.js origin)        │   │
│  └──────────┘  └────────┬────────┘  └──────────────────────────┘   │
│                          │                                           │
│                  ┌───────┴──────────┐                               │
│                  │  services/       │                               │
│                  │  csv_processor   │                               │
│                  └──────────────────┘                               │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     ADAPTIVE DATA ENGINE                             │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  LLM Abstraction Layer                                       │    │
│  │                                                              │    │
│  │  LLMFactory ──► GeminiProvider  (google-genai)              │    │
│  │             ──► OpenAIProvider  (openai + tenacity)          │    │
│  │             ──► AnthropicProvider                            │    │
│  │             ──► OllamaProvider  (local)                      │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Benchmark Generation Pipeline                               │    │
│  │                                                              │    │
│  │  BenchmarkPromptBuilder                                      │    │
│  │    → LLMBenchmarkGenerator (async, retry, temp nudging)      │    │
│  │      → BenchmarkResponseParser                               │    │
│  │        → BenchmarkQualityScorer                              │    │
│  │          → BenchmarkDeduplicator                             │    │
│  │            → BenchmarkValidator                              │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  11-Stage Master Orchestrator                                │    │
│  │  DatasetGenomeMasterPipeline                                 │    │
│  │                                                              │    │
│  │  Stage 1: Init     Stage 5: Quality   Stage  9: Parquet     │    │
│  │  Stage 2: LLM      Stage 6: JSON      Stage 10: HF Export   │    │
│  │  Stage 3: Generate Stage 7: JSONL     Stage 11: Reports     │    │
│  │  Stage 4: Validate Stage 8: CSV                             │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      EXPORT & PUBLICATION                            │
│                                                                      │
│  export_benchmark/                                                   │
│  ├── benchmark_v1.0.jsonl      (200 samples, training format)       │
│  ├── benchmark_v1.0.json       (structured archive)                  │
│  ├── benchmark_v1.0.csv        (tabular)                             │
│  ├── benchmark_v1.0.parquet    (columnar)                            │
│  ├── benchmark_report.json     (quality metrics)                     │
│  └── reproducibility_manifest.json                                   │
│                                                                      │
│  publication/huggingface/ ──► 🤗 HuggingFace Dataset Hub            │
│  publication/model/       ──► 🤗 HuggingFace Model Hub              │
│  publication/kaggle/      ──► 📊 Kaggle Dataset Hub                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Component Reference

### Backend Modules (`backend/app/`)

| Module | Path | Responsibility |
|--------|------|----------------|
| **LLM Layer** | `app/llm/` | Provider abstraction, factory, models, config |
| **Benchmark** | `app/benchmark/` | Sample generation, prompts, parsing, scoring, validation |
| **Dataset Generator** | `app/dataset_generator/` | Template-based baseline generator |
| **Pipeline** | `app/pipeline/` | Master orchestrator (11 stages) |
| **Publication** | `app/publication/` | Export formatters (JSONL, CSV, Parquet, HF) |
| **Adaptive Data** | `app/adaptive_data/` | Adaptive scoring and data engine |
| **Research** | `app/research/` | Research gap analysis modules |
| **Evaluation** | `app/evaluation/` | Model evaluation utilities |
| **Integrations** | `app/integrations/` | HuggingFace + Kaggle API clients |

### Services (`backend/services/`)

| Service | Responsibility |
|---------|----------------|
| `autoscientist/` | AutoScientist reasoning pipeline coordination |
| `dataset_intelligence/` | Dataset analysis and intelligence scoring |
| `csv_processor.py` | CSV upload processing (API endpoint handler) |

### API Layer (`backend/api/`)

| Route | Method | Description |
|-------|--------|-------------|
| `/health` | GET | API health check and version |
| `/upload` | POST | CSV file upload with metadata extraction |

---

## Data Flow

```
.env (API keys)
    │
    ▼
LLMConfig ──► LLMFactory ──► Provider (Gemini / OpenAI)
                                  │
                                  ▼
BenchmarkPromptBuilder ──► LLMRequest
                                  │
                          LLMBenchmarkGenerator
                                  │
                                  ▼
                      BenchmarkResponseParser
                                  │
                          BenchmarkSample
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼              ▼
             QualityScorer  Deduplicator    Validator
                    │
              BenchmarkSuite (200 samples)
                    │
        ┌───────────┼───────────┬──────────┐
        ▼           ▼           ▼          ▼
      JSONL        JSON        CSV      Parquet
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend API | FastAPI | 0.115 | REST API and middleware |
| ASGI Server | Uvicorn | 0.32 | Production-grade async server |
| Data Validation | Pydantic | 2.x | Schema validation and settings |
| Frontend | Next.js | 15 | React-based dashboard |
| Type System | TypeScript | 5 | Frontend type safety |
| LLM (primary) | Google Gemini | 2.0-flash | Dataset generation |
| LLM (fallback) | OpenAI | GPT-4o | Alternative provider |
| Retry Logic | Tenacity | 9.x | Exponential backoff on LLM calls |
| ML Training | PEFT + LoRA | 0.14+ | Parameter-efficient fine-tuning |
| Columnar Storage | PyArrow | 18.x | Parquet export |
| Testing | Pytest | 8.x | 188 backend tests |

---

## Security Architecture

- **API keys** read exclusively from environment variables (never hardcoded)
- **CORS** restricted to configured frontend origins
- **File uploads** validated for type (CSV only) and size (50 MB max)
- **Generated exports** scanned before publication (no secret leakage)
- **`.env` files** excluded from git via `.gitignore`

---

*For the end-to-end flow with Mermaid diagrams, see [`project_flow.md`](project_flow.md). For the dataset schema, see [`dataset.md`](dataset.md).*

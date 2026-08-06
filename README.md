<div align="center">

# 🧬 Dataset Genome

### Autonomous Scientific Reasoning Dataset & AutoScientist Benchmark Pipeline

**HackIndia 2026 AutoScientist Challenge — Official Submission**

---

[![HackIndia 2026](https://img.shields.io/badge/HackIndia-2026%20AutoScientist-blueviolet?style=for-the-badge&logo=rocket)](https://hackindia.xyz)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org)

[![HuggingFace Dataset](https://img.shields.io/badge/🤗%20Dataset-Agriculture%20Benchmark-orange?style=for-the-badge)](https://huggingface.co/datasets/YOUR-HF-USERNAME/dataset-genome-agriculture-mechanism-outcomes)
[![HuggingFace Model](https://img.shields.io/badge/🤗%20Model-AutoScientist-orange?style=for-the-badge)](https://huggingface.co/YOUR-HF-USERNAME/autoscientist-reasoning-model)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20BEFF?style=for-the-badge&logo=kaggle)](https://kaggle.com/datasets/YOUR-KAGGLE-USERNAME/dataset-genome-agriculture)

[![Benchmark Score](https://img.shields.io/badge/Benchmark%20Score-88.3%2F100-brightgreen?style=for-the-badge)](export_benchmark/benchmark_report.md)
[![Tests](https://img.shields.io/badge/Tests-188%20Passing-brightgreen?style=for-the-badge)](backend/)
[![Domains](https://img.shields.io/badge/Scientific%20Domains-10-blue?style=for-the-badge)](docs/benchmark.md)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Architecture](#️-architecture)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Dataset](#-dataset)
- [Training Pipeline](#-training-pipeline)
- [Benchmark Results](#-benchmark-results)
- [Publication Links](#-publication-links)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Future Work](#-future-work)
- [License](#-license)

---

## 🔬 Overview

**Dataset Genome** is an end-to-end autonomous scientific reasoning platform that generates, validates, and publishes structured benchmark datasets for training AI models on complex scientific reasoning tasks.

Built for the **HackIndia 2026 AutoScientist Challenge**, this project implements the complete pipeline from raw scientific data to a fine-tuned AutoScientist model, published across HuggingFace and Kaggle.

> **Core Innovation:** The **Adaptive Data Engine** — a multi-stage pipeline that generates scientifically rigorous prompt–completion pairs using LLM orchestration, validates them through automated quality scoring, and exports them in publication-ready formats.

---

## 🎯 Problem Statement

### Why Existing Datasets Are Insufficient

Current scientific reasoning datasets suffer from:

| Limitation | Impact |
|---|---|
| **Narrow domain coverage** | Models fail to generalize across scientific disciplines |
| **Shallow reasoning chains** | Datasets lack hypothesis-experiment-conclusion structure |
| **No adaptive scoring** | No mechanism to measure dataset quality before training |
| **Manual curation** | Not scalable to the volume needed for modern LLM training |
| **No reproducibility** | Missing manifests, random seeds, and lineage tracking |

### Our Solution

Dataset Genome addresses all of these through:

- **Autonomous generation** via LLM orchestration (Gemini, OpenAI, Anthropic)
- **10-point structured reasoning chains** per sample (observation → hypothesis → experiment → conclusion)
- **Adaptive scoring** with a composite quality metric (88.3/100 achieved)
- **Built-in deduplication** and validation before export
- **Full reproducibility manifests** with git hashes, seeds, and prompt versions

---

## 🏗️ Architecture

```
                    Raw Scientific Scenario Seeds
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Adaptive Data      │
                    │  Engine             │  ← LLM Orchestration
                    │  (LLMFactory +      │     (Gemini / OpenAI)
                    │   BenchmarkPrompt   │
                    │   Builder)          │
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │  Dataset Genome     │
                    │  Pipeline           │  ← 200 Samples
                    │  (11-Stage Master   │     10 Domains
                    │   Orchestrator)     │     4 Difficulty Levels
                    └────────┬────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
           ┌──────────────┐  ┌──────────────────┐
           │  Validation  │  │  Quality Scorer  │
           │  Pipeline    │  │  (Adaptive Score │
           │  (Dedup +    │  │   88.3 / 100)    │
           │   Balance)   │  └──────────────────┘
           └──────┬───────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Training       │
         │  Dataset        │  ← 20 Agriculture Records (HF Release)
         │  (JSONL)        │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  AutoScientist  │  ← LoRA Fine-tuning
         │  Model          │     via PEFT
         └────────┬────────┘
                  │
        ┌─────────┼──────────┐
        ▼         ▼          ▼
 ┌──────────┐ ┌────────┐ ┌────────┐
 │HuggingFace│ │HF Model│ │Kaggle  │
 │ Dataset  │ │        │ │Dataset │
 └──────────┘ └────────┘ └────────┘
```

### System Components

| Component | Technology | Purpose |
|---|---|---|
| **Backend API** | FastAPI + Python 3.12 | REST API, file processing, pipeline orchestration |
| **Frontend Dashboard** | Next.js 15 + TypeScript | Live benchmark monitoring and dataset visualization |
| **LLM Layer** | google-genai, openai, anthropic | Multi-provider LLM abstraction with failover |
| **Adaptive Data Engine** | Custom Python | Dataset generation, scoring, deduplication |
| **Publication Pipeline** | HuggingFace Hub, Kaggle API | Automated dataset and model publishing |

---

## ✨ Key Features

### 🤖 Adaptive Data Engine
Autonomous dataset generation using a multi-provider LLM abstraction layer (`LLMFactory`). Supports Gemini, OpenAI, Anthropic, and Ollama with automatic failover and retry logic.

### 🧪 Scientific Reasoning Dataset
200-sample benchmark spanning **10 scientific domains** (Agriculture, Healthcare, Climate Science, Biology, Chemistry, Physics, Mathematics, Finance, HR, Market Analysis) across **4 difficulty levels** (Easy → Expert).

### ✅ Automated Validation Pipeline
Built-in duplicate detection, domain/difficulty balance checks, and reasoning chain completeness scoring before any export.

### 📊 Adaptive Quality Scoring
Composite quality metric combining knowledge coverage, reasoning completeness, experiment design diversity, and failure mode diversity. Current score: **88.3 / 100**.

### 🔄 Multi-Format Export
Simultaneous export to `JSON`, `JSONL`, `CSV`, `Parquet`, `HuggingFace`, and dashboard analytics formats.

### 🤗 HuggingFace Publication Pipeline
Automated dataset card generation, metadata validation, and `huggingface-cli` upload to the Hub.

### 📈 Kaggle Integration
Dataset packaging and `kaggle` API publication workflow.

### 🔬 AutoScientist Training
LoRA fine-tuning via PEFT on GPT-class models using the generated dataset. Full training configuration in [`docs/training.md`](docs/training.md).

### 📋 Benchmark Reports
Automated versioned benchmark reports with lineage tracking, reproducibility manifests, and leaderboard generation.

---

## 📁 Project Structure

```
dataset_genome/
│
├── 📄 README.md                    # This file
├── 📄 demo.py                      # Full end-to-end demonstration script
├── 📄 requirements.txt             # Root pipeline dependencies
├── 📄 .env.example                 # Environment variable template
├── 📄 sample_dataset.csv           # Sample Agriculture dataset
├── 📄 BACKEND_FREEZE.md            # Backend stability notice
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 CODE_OF_CONDUCT.md           # Community standards
├── 📄 SECURITY.md                  # Security policy
│
├── 🐍 backend/                     # Python FastAPI backend
│   ├── main.py                     # FastAPI app entry point
│   ├── requirements.txt            # Backend API dependencies
│   ├── api/                        # REST API routes
│   │   └── routes/                 # health, upload endpoints
│   ├── app/                        # Core application modules
│   │   ├── adaptive_data/          # Adaptive Data Engine
│   │   ├── benchmark/              # Benchmark generation & scoring
│   │   │   ├── llm_generator.py    # Async LLM benchmark generator
│   │   │   ├── prompt_builder.py   # Scientific prompt construction
│   │   │   ├── validator.py        # Suite validation
│   │   │   └── quality_scorer.py   # Adaptive quality scoring
│   │   ├── dataset_generator/      # Template-based dataset generation
│   │   ├── llm/                    # LLM provider abstraction layer
│   │   │   ├── factory.py          # LLMFactory (provider registry)
│   │   │   ├── providers/          # Gemini, OpenAI, Anthropic, Ollama
│   │   │   └── config.py           # LLMConfig (reads from .env)
│   │   ├── pipeline/               # Master orchestrator (11 stages)
│   │   └── publication/            # Export formatters
│   ├── services/                   # AutoScientist & CSV services
│   └── tests/                      # 188 tests (pytest)
│
├── 🌐 frontend/                    # Next.js 15 dashboard
│   └── src/
│       ├── app/                    # App Router pages
│       ├── components/             # React UI components
│       └── lib/                   # Typed API client
│
├── 📊 datasets/                    # Dataset storage
│   ├── raw/                        # Original generated records
│   ├── evolved/                    # Post-adaptive processing
│   ├── final/                      # Publication-ready splits
│   └── metadata/                   # Dataset lineage metadata
│
├── 📈 export_benchmark/            # Benchmark outputs (generated)
│   ├── benchmark_v1.0.jsonl        # Full 200-sample benchmark
│   ├── benchmark_v1.0.csv          # CSV format
│   ├── benchmark_v1.0.parquet      # Parquet format
│   ├── benchmark_report.md         # Human-readable report
│   └── benchmark_report.json       # Machine-readable report
│
├── 🤗 publication/                 # Publication pipeline
│   ├── huggingface/                # HF dataset package
│   │   ├── README.md               # HF dataset card
│   │   ├── train.jsonl             # 20-sample Agriculture release
│   │   └── dataset_info.json       # HF metadata spec
│   ├── kaggle/                     # Kaggle dataset package
│   ├── model/                      # Model card & weights ref
│   └── reports/                    # Release reports
│
└── 📚 docs/                        # Technical documentation
    ├── architecture.md             # System architecture
    ├── dataset.md                  # Dataset schema & methodology
    ├── training.md                 # AutoScientist training guide
    ├── benchmark.md                # Benchmark methodology & results
    ├── publication.md              # HuggingFace & Kaggle publishing
    ├── project_flow.md             # End-to-end project flow
    ├── research-gap.md             # Research motivation
    ├── roadmap.md                  # Future development roadmap
    └── vision.md                   # Project vision
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Required For |
|------|---------|-------------|
| Python | 3.12+ | Backend, Pipeline, Demo |
| Node.js | 18+ | Frontend Dashboard |
| npm | 9+ | Frontend |
| Git | 2.x+ | All |

### 1. Clone & Setup

```bash
git clone https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes.git
cd adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.example .env

# Fill in your API keys
# GOOGLE_API_KEY=your_key_here        (for Gemini — primary provider)
# OPENAI_API_KEY=your_key_here        (optional — fallback provider)
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 4. Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at: **http://localhost:3000**

### 5. Run the Full Demo Pipeline

```bash
# From repository root (with backend venv active)
cd ..
pip install -r requirements.txt
python demo.py
```

This executes the complete 11-stage pipeline and generates all benchmark outputs in `export_benchmark/`.

---

## 📊 Dataset

Dataset Genome generates structured scientific reasoning records with **10 fields per sample**, following a standardized schema designed for hypothesis-driven AI training.

### Sample Record

```json
{
  "id": "rec-agriculture-001-44863d",
  "domain": "Agriculture",
  "difficulty": "hard",
  "prompt": "Evaluate scientific dataset anomaly in Agriculture: Unexpected 14% drop in crop yield despite optimal nitrogen fertilizer application. Formulate primary hypothesis and experimental validation design.",
  "context": "Soil moisture and crop yield telemetry collected across 500 agricultural test plots.",
  "observation": "Unexpected 14% drop in crop yield despite optimal nitrogen fertilizer application.",
  "identified_problem": "Micro-nutrient imbalance (Zinc deficiency) inhibiting nitrogen absorption.",
  "research_gap": "Lack of real-time multi-spectral soil mineral interaction modeling.",
  "primary_hypothesis": "Foliar application of chelated zinc will restore nitrogen uptake and increase yield by >= 10%.",
  "alternative_hypothesis": "Soil compaction is restricting root growth independently of mineral availability.",
  "experiment_design": "Split-plot randomized control trial applying 2.5 kg/ha chelated zinc vs baseline control.",
  "control_variables": ["Nitrogen application rate", "Irrigation volume", "Solar radiation"],
  "evaluation_metrics": ["yield_per_hectare", "leaf_zinc_concentration", "nitrogen_use_efficiency"],
  "expected_result": "Leaf zinc concentration increases above 25 ppm, boosting crop yield by 12%.",
  "failure_cases": ["Heavy rainfall leaching foliar spray", "Soil pH below 5.5 locking zinc availability"],
  "scientific_conclusion": "Zinc supplementation resolves micronutrient bottleneck and maximizes nitrogen fertilizer efficiency.",
  "created_at": "2026-08-03 15:22:00"
}
```

### Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record identifier |
| `domain` | string | Scientific domain (Agriculture, Biology, etc.) |
| `difficulty` | string | Easy / Medium / Hard / Expert |
| `prompt` | string | The reasoning challenge prompt |
| `context` | string | Background experimental context |
| `observation` | string | Observed anomaly or phenomenon |
| `identified_problem` | string | Root cause identification |
| `research_gap` | string | Gap in existing literature |
| `primary_hypothesis` | string | Main testable hypothesis |
| `alternative_hypothesis` | string | Competing explanation |
| `experiment_design` | string | Proposed experimental methodology |
| `control_variables` | list[str] | Variables held constant |
| `evaluation_metrics` | list[str] | Measurable outcome metrics |
| `expected_result` | string | Predicted experimental outcome |
| `failure_cases` | list[str] | Known failure modes |
| `scientific_conclusion` | string | Conclusion drawn from experiment |

→ Full schema documentation: [`docs/dataset.md`](docs/dataset.md)

---

## 🧠 Training Pipeline

Dataset Genome trains the **AutoScientist** model using LoRA-based parameter-efficient fine-tuning (PEFT) on the generated dataset.

```
Generated Dataset (JSONL)
        │
        ▼
Adaption Adaptive Data Processing
        │
        ▼
LoRA Configuration (PEFT)
        │
        ▼
GPT-class Base Model
        │
        ▼
AutoScientist Fine-tuned Model
        │
        ▼
HuggingFace Model Hub
```

Key training parameters:
- **Method:** LoRA (Low-Rank Adaptation)
- **Library:** PEFT (HuggingFace)
- **Task:** Causal Language Modeling / Scientific Reasoning
- **Dataset:** Agriculture mechanism outcomes (20 records, v1.0 release)

→ Full training documentation: [`docs/training.md`](docs/training.md)

---

## 📈 Benchmark Results

Official benchmark results for Dataset Genome v1.0:

| Metric | Value |
|--------|-------|
| **Total Benchmark Samples** | 200 |
| **Scientific Domains** | 10 |
| **Difficulty Levels** | 4 (Easy → Expert) |
| **Composite Adaptive Score** | **88.3 / 100** |
| **Knowledge Coverage** | 100.0% |
| **Reasoning Chain Completeness** | 100.0% |
| **Duplicate Samples** | 0 |
| **Validation Status** | ✅ PASSED |

### Domain Distribution (200 samples, balanced)

| Domain | Samples |
|--------|---------|
| Agriculture | 20 |
| Healthcare | 20 |
| Climate Science | 20 |
| Biology | 20 |
| Chemistry | 20 |
| Physics | 20 |
| Mathematics | 20 |
| Finance | 20 |
| HR | 20 |
| Market Analysis | 20 |

→ Full benchmark report: [`export_benchmark/benchmark_report.md`](export_benchmark/benchmark_report.md)

---

## 🔗 Publication Links

| Resource | Link |
|----------|------|
| 🤗 **HuggingFace Dataset** | [dataset-genome-agriculture-mechanism-outcomes](https://huggingface.co/datasets/surabhi08/dataset-genome-agriculture-benchmark) |
| 🤗 **HuggingFace Model** | [autoscientist-reasoning-model](https://huggingface.co/surabhi08/dataset-genome-agriculture-benchmark-model) |
| 📊 **Kaggle Dataset** | [dataset-genome-agriculture](https://www.kaggle.com/datasets/surabhinikam/dataset-genome-agriculture-benchmark) |
| 📄 **Benchmark Report** | [`export_benchmark/benchmark_report.md`](export_benchmark/benchmark_report.md) |
| 🏆 **HackIndia Challenge** | [AutoScientist Challenge Part 2](https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes) |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | Full system architecture and component design |
| [`docs/dataset.md`](docs/dataset.md) | Dataset schema, methodology, and generation pipeline |
| [`docs/training.md`](docs/training.md) | AutoScientist training — PEFT, LoRA, GPT-OSS |
| [`docs/benchmark.md`](docs/benchmark.md) | Benchmark methodology, scoring, and results |
| [`docs/publication.md`](docs/publication.md) | HuggingFace and Kaggle publication guide |
| [`docs/project_flow.md`](docs/project_flow.md) | End-to-end project flow with Mermaid diagrams |
| [`docs/research-gap.md`](docs/research-gap.md) | Research motivation and problem analysis |
| [`docs/roadmap.md`](docs/roadmap.md) | Future development roadmap |

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 🔭 Future Work

- [ ] Expand HuggingFace release to all 10 scientific domains
- [ ] Automated retraining pipeline on new dataset versions
- [ ] Real-time scientific literature integration (ArXiv, PubMed)
- [ ] Web-based dataset generation interface
- [ ] Collaborative annotation and human-in-the-loop validation
- [ ] Multi-modal scientific reasoning (images, charts, tables)
- [ ] Integration with scientific simulation environments

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

```
MIT License
Copyright (c) 2026 Surabhi M. S. (HackIndia Challenge Submission)
```

---

<div align="center">

**Built with ❤️ for HackIndia 2026 AutoScientist Challenge**

*Dataset Genome — Autonomous Scientific Reasoning at Scale*

</div>

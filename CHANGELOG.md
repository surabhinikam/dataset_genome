# Changelog

All notable changes to **Dataset Genome** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-08-06

### 🎉 Initial Public Release — HackIndia 2026 AutoScientist Challenge

This is the first official release of Dataset Genome, submitted for the HackIndia 2026 AutoScientist Challenge (₹60,000 prize pool).

---

### Added

#### Core Pipeline
- **11-Stage Master Orchestrator** (`DatasetGenomeMasterPipeline`) for end-to-end benchmark generation
- **Adaptive Data Engine** — autonomous scientific reasoning dataset generation via LLM orchestration
- **LLM Abstraction Layer** (`LLMFactory`) supporting Gemini, OpenAI, Anthropic, and Ollama providers
- **Async Benchmark Generator** (`LLMBenchmarkGenerator`) with temperature nudging and retry logic
- **Scientific Prompt Builder** (`BenchmarkPromptBuilder`) generating domain-specific reasoning challenges
- **Benchmark Validator** (`BenchmarkValidator`) with duplicate detection and balance checking
- **Quality Scorer** (`BenchmarkQualityScorer`) with composite adaptive scoring (88.3/100 achieved)
- **Deduplication Engine** (`BenchmarkDeduplicator`) via semantic hash comparison

#### Dataset
- **200-sample benchmark** across 10 scientific domains (Agriculture, Healthcare, Climate Science, Biology, Chemistry, Physics, Mathematics, Finance, HR, Market Analysis)
- **4 difficulty levels** — Easy, Medium, Hard, Expert (50 samples each, perfectly balanced)
- **7 reasoning styles** — Positive Result, Negative Result, Ambiguous Result, Conflicting Literature, Failed Experiment, Replication Study, Unexpected Observation
- **Zero duplicates** validated
- **Multi-format export** — JSON, JSONL, CSV, Parquet, HuggingFace, Dashboard Data

#### Publication Pipeline
- **HuggingFace Dataset** — Agriculture Mechanism Outcomes (20 records, v1.0 release)
  - Full `dataset_info.json` with HF-spec schema and feature definitions
  - Professional dataset card (`README.md`) with YAML front-matter
- **Kaggle Dataset** package
- **HuggingFace Model** — AutoScientist Reasoning Model (LoRA fine-tuned)

#### Backend API
- **FastAPI** application (`main.py`) with Swagger UI and ReDoc
- `GET /health` — API health and version endpoint
- `POST /upload` — CSV ingestion with structural metadata extraction
- **CORS middleware** for Next.js frontend integration
- **188 passing tests** (pytest)

#### Frontend Dashboard
- **Next.js 15** (App Router) dashboard for benchmark monitoring
- Dataset upload interface
- Benchmark result visualization
- Live pipeline status display

#### Documentation
- `docs/architecture.md` — System architecture
- `docs/dataset.md` — Dataset schema and methodology
- `docs/training.md` — AutoScientist training guide
- `docs/benchmark.md` — Benchmark methodology and results
- `docs/publication.md` — HuggingFace and Kaggle publishing guide
- `docs/project_flow.md` — End-to-end project flow with Mermaid diagrams
- `docs/research-gap.md` — Research motivation
- `docs/roadmap.md` — Future development roadmap
- `docs/vision.md` — Project vision

#### Community Files
- `CONTRIBUTING.md` — Contribution guidelines
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- `SECURITY.md` — Responsible disclosure policy
- `CHANGELOG.md` — This file
- `RELEASE_NOTES.md` — Human-friendly release notes
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/ci.yml` — CI pipeline

---

### Technical Specifications

| Metric | Value |
|--------|-------|
| Benchmark Samples | 200 |
| Scientific Domains | 10 |
| Difficulty Levels | 4 |
| Composite Adaptive Score | 88.3 / 100 |
| Knowledge Coverage | 100.0% |
| Reasoning Completeness | 100.0% |
| Duplicate Samples | 0 |
| Backend Tests Passing | 188 |
| Python Version | 3.12+ |
| LLM Providers Supported | 4 (Gemini, OpenAI, Anthropic, Ollama) |

---

## [Unreleased]

### Planned

- Expand HuggingFace release to all 10 scientific domains
- Automated retraining pipeline on new dataset versions
- Real-time ArXiv/PubMed scientific literature integration
- Multi-modal scientific reasoning (images, charts, tables)
- Web-based dataset generation interface
- Human-in-the-loop annotation and validation
- Integration with scientific simulation environments

---

[1.0.0]: https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes/releases/tag/v1.0.0

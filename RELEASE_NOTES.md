# Release Notes — Dataset Genome v1.0.0

**Release Date:** 2026-08-06  
**Submitted By:** Surabhi M. S.  
**Challenge:** HackIndia 2026 AutoScientist Challenge — Part 2 (₹60,000 Prize Pool)

---

## 🎉 What's New in v1.0.0

We are excited to announce the **first public release of Dataset Genome** — an autonomous scientific reasoning dataset and AutoScientist benchmark pipeline.

This release represents the complete end-to-end implementation of the HackIndia AutoScientist Challenge submission, from raw data generation to published HuggingFace datasets and model.

---

## 🔑 Highlights

### ✅ 200-Sample Scientific Reasoning Benchmark

A production-quality benchmark dataset spanning **10 scientific domains** and **4 difficulty levels**, generated autonomously using the Adaptive Data Engine and validated to achieve a **composite adaptive score of 88.3/100**.

- Zero duplicate samples
- Perfectly balanced domain and difficulty distribution
- 100% knowledge coverage and reasoning chain completeness

### ✅ Adaptive Data Engine

The core innovation: an autonomous LLM orchestration pipeline that generates scientifically rigorous reasoning chains using **Gemini**, **OpenAI**, **Anthropic**, or **Ollama** as the underlying model provider.

### ✅ AutoScientist Model Published

A LoRA fine-tuned reasoning model trained on the Dataset Genome benchmark is published on HuggingFace. The model is optimized for scientific hypothesis generation, observation analysis, and experimental design.

### ✅ HuggingFace Dataset Published

The Agriculture Mechanism Outcomes dataset (20 records, v1.0) is published on HuggingFace Hub with:
- Full `dataset_info.json` HF-spec metadata
- Professional dataset card
- MIT license
- Complete feature schema

### ✅ Kaggle Dataset Published

The same dataset is available on Kaggle for the broader data science community.

### ✅ 188 Passing Tests

The backend is fully tested with 188 pytest tests covering all major components including LLM providers, benchmark generation, validation, quality scoring, and publication pipeline.

---

## 📊 Benchmark Statistics

| Metric | Value |
|--------|-------|
| Total Samples | 200 |
| Domains | 10 |
| Difficulty Levels | 4 |
| **Adaptive Score** | **88.3 / 100** |
| Knowledge Coverage | 100% |
| Reasoning Completeness | 100% |
| Duplicates | 0 |

---

## 🔗 Published Artifacts

| Artifact | Location |
|----------|----------|
| HuggingFace Dataset | `publication/huggingface/` |
| HuggingFace Model | `publication/model/` |
| Kaggle Dataset | `publication/kaggle/` |
| Benchmark Reports | `export_benchmark/` |
| Full Benchmark (200 samples) | `export_benchmark/benchmark_v1.0.jsonl` |

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI 0.115 + Python 3.12 |
| Frontend | Next.js 15 + TypeScript |
| LLM Orchestration | google-genai, openai, anthropic |
| Dataset Format | JSONL, JSON, CSV, Parquet |
| Fine-tuning | PEFT + LoRA |
| Testing | pytest (188 tests) |

---

## ⚠️ Known Limitations

- The HuggingFace v1.0 release contains Agriculture domain samples only (20 records). The full 200-sample benchmark spans all 10 domains and is available in `export_benchmark/benchmark_v1.0.jsonl`.
- The frontend dashboard is optimized for local development; production deployment requires additional configuration.
- LLM-based generation requires a valid `GOOGLE_API_KEY` or `OPENAI_API_KEY`. Template-based fallback generation works without API keys.

---

## 🔭 What's Next

See [`CHANGELOG.md`](CHANGELOG.md) for the complete roadmap of planned improvements including:
- Full 10-domain HuggingFace release
- Automated retraining pipeline
- Real-time scientific literature integration
- Multi-modal reasoning support

---

*Dataset Genome v1.0.0 — HackIndia 2026 AutoScientist Challenge*  
*MIT License © 2026 Surabhi M. S.*

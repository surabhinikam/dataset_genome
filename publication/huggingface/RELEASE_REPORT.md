# Dataset Genome — HuggingFace Release Report

**Release Date:** 2026-08-06  
**Dataset Name:** Dataset Genome - Agriculture Mechanism Outcomes  
**Release Version:** v1.0.0  
**Prepared By:** Surabhi M. S. (HackIndia Challenge Submission)  
**Repository:** https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes

---

## Dataset Summary

The v1.0 public release contains Agriculture scientific reasoning records. Future versions may expand into additional scientific domains.

---

## Files Included in HuggingFace Package

| File | Size | Status |
|------|------|--------|
| `train.jsonl` | 31,902 bytes | ✅ Included |
| `README.md` | — | ✅ Included |
| `LICENSE` | 1,102 bytes | ✅ Included (Full MIT) |
| `dataset_info.json` | — | ✅ Included (Updated) |
| `DATASET_CARD.md` | — | ✅ Included |
| `MODEL_CARD.md` | — | ✅ Included |
| `config.json` | 131 bytes | ✅ Included |

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total samples | **20** |
| Training samples | 20 |
| Validation samples | 0 (not split) |
| Test samples | 0 (not split) |
| File format | JSONL (UTF-8) |
| File size | 31,902 bytes |
| Language | English |
| License | MIT |

### Domain Distribution

| Domain | Count | Percentage |
|--------|-------|-----------|
| Agriculture | 20 | 100% |

### Difficulty Distribution

| Difficulty | Count | Percentage |
|-----------|-------|-----------|
| hard | 10 | 50% |
| medium | 10 | 50% |

### Dataset Schema Fields

Each JSONL record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record identifier |
| `domain` | string | Scientific domain (Agriculture) |
| `difficulty` | string | Difficulty level (medium, hard) |
| `prompt` | string | Input prompt for the model |
| `context` | string | Background context |
| `observation` | string | Observed anomaly or phenomenon |
| `identified_problem` | string | Root cause identification |
| `research_gap` | string | Gap in existing literature |
| `primary_hypothesis` | string | Main experimental hypothesis |
| `alternative_hypothesis` | string | Alternative explanation |
| `experiment_design` | string | Proposed experimental design |
| `control_variables` | list[string] | Variables held constant |
| `evaluation_metrics` | list[string] | Metrics to measure outcomes |
| `expected_result` | string | Predicted experimental outcome |
| `failure_cases` | list[string] | Known failure modes |
| `scientific_conclusion` | string | Conclusion drawn from experiment |
| `created_at` | string | Generation timestamp |

---

## Files Created / Modified in This Release

| File | Action |
|------|--------|
| `publication/huggingface/dataset_info.json` | **UPDATED** — Full HuggingFace-spec JSON; name, description, tags, citation corrected to Agriculture-only |
| `publication/huggingface/LICENSE` | **UPDATED** — Full MIT License with correct copyright |
| `publication/huggingface/README.md` | **UPDATED** — Title, overview, domain stats corrected to Agriculture-only |
| `publication/huggingface/DATASET_CARD.md` | **UPDATED** — License, version, domain count, author corrected |
| `publication/huggingface/MODEL_CARD.md` | **UPDATED** — License corrected to MIT; author updated |
| `LICENSE` (root) | **MODIFIED** — Copyright: `HackIndia` → `Surabhi M. S. (HackIndia Challenge Submission)` |

---

## Release Readiness Checklist

| Check | Result |
|-------|--------|
| ✅ `train.jsonl` exists | PASS |
| ✅ `train.jsonl` is non-empty (20 samples, 31,902 bytes) | PASS |
| ✅ `README.md` exists | PASS |
| ✅ `LICENSE` exists and is full MIT | PASS |
| ✅ `dataset_info.json` exists and is HF-spec | PASS |
| ✅ No `.env` file present | PASS |
| ✅ No API keys detected | PASS |
| ✅ No `*.safetensors` files | PASS |
| ✅ No `node_modules` | PASS |
| ✅ No `.venv` directory | PASS |
| ✅ No `__pycache__` directories | PASS |
| ✅ License consistent (MIT) across all metadata files | PASS |
| ✅ Copyright line corrected | PASS |
| ✅ No "Healthcare" in metadata or documentation | PASS |
| ✅ Domain distribution consistent with train.jsonl | PASS |

**All 15 checks passed.**

---

## HuggingFace Publication Checklist

Before running `huggingface-cli upload`, verify:

- [ ] Create a HuggingFace account / log in: `huggingface-cli login`
- [ ] Create a new dataset repository named `dataset-genome-agriculture-mechanism-outcomes`
- [ ] Confirm the dataset repository name matches `dataset_info.json` → `name` field
- [ ] Run: `huggingface-cli upload <your-hf-username>/dataset-genome-agriculture-mechanism-outcomes publication/huggingface/ --repo-type dataset`
- [ ] Verify the dataset card renders correctly on HuggingFace Hub
- [ ] Tag the release as `v1.0.0`

---

## Integrity Summary

| Metric | Value |
|--------|-------|
| Backend code modified | **None** |
| Frontend code modified | **None** |
| Dataset generation modified | **None** |
| `train.jsonl` modified | **None** |
| Benchmark outputs modified | **None** |
| Dataset records modified | **None** |

---

*Generated by Dataset Genome Release Engineer — HackIndia AutoScientist Challenge 2026*

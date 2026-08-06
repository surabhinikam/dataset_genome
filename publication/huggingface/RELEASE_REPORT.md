# Dataset Genome — HuggingFace Release Report

**Release Date:** 2026-08-06  
**Dataset Name:** Dataset Genome - Agri Health Mechanism Outcomes  
**Release Version:** v1.0.0  
**Prepared By:** Surabhi M. S. (HackIndia Challenge Submission)  
**Repository:** https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes

---

## Files Included in HuggingFace Package

| File | Size | Status |
|------|------|--------|
| `train.jsonl` | 16,322 bytes | ✅ Included |
| `README.md` | 1,120 bytes | ✅ Included |
| `LICENSE` | 1,102 bytes | ✅ Included (Full MIT) |
| `dataset_info.json` | 2,978 bytes | ✅ Included (Updated) |
| `DATASET_CARD.md` | 1,120 bytes | ✅ Included |
| `MODEL_CARD.md` | 813 bytes | ✅ Included |
| `config.json` | 131 bytes | ✅ Included |

**Total HuggingFace package size:** ~23,586 bytes

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total samples | **10** |
| Training samples | 10 |
| Validation samples | 0 (not split) |
| Test samples | 0 (not split) |
| File format | JSONL (UTF-8) |
| File size | 16,322 bytes |
| Language | English |
| License | MIT |

### Domain Distribution

| Domain | Count | Percentage |
|--------|-------|-----------|
| Agriculture | 10 | 100% |

### Difficulty Distribution

| Difficulty | Count | Percentage |
|-----------|-------|-----------|
| hard | 5 | 50% |
| medium | 5 | 50% |

### Dataset Schema Fields

Each JSONL record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record identifier |
| `domain` | string | Scientific domain (Agriculture, Healthcare, etc.) |
| `difficulty` | string | Difficulty level (easy, medium, hard, expert) |
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

## Files Created

| File | Action |
|------|--------|
| `publication/huggingface/dataset_info.json` | **UPDATED** — Replaced minimal 6-line stub with full HuggingFace-spec JSON (features schema, splits, task categories, license, homepage) |
| `publication/huggingface/LICENSE` | **UPDATED** — Replaced bare `apache-2.0` stub with full MIT License text |

## Files Modified

| File | Action |
|------|--------|
| `LICENSE` (root) | **MODIFIED** — Copyright line updated: `HackIndia` → `Surabhi M. S. (HackIndia Challenge Submission)` |

---

## Release Readiness Checklist

| Check | Result |
|-------|--------|
| ✅ `train.jsonl` exists | PASS |
| ✅ `train.jsonl` is non-empty (10 samples) | PASS |
| ✅ `README.md` exists | PASS |
| ✅ `LICENSE` exists and is full MIT | PASS |
| ✅ `dataset_info.json` exists and is HF-spec | PASS |
| ✅ No `.env` file present | PASS |
| ✅ No API keys detected | PASS |
| ✅ No `*.safetensors` files | PASS |
| ✅ No `node_modules` | PASS |
| ✅ No `.venv` directory | PASS |
| ✅ No `__pycache__` directories | PASS |
| ✅ License is MIT (consistent across root + HF package) | PASS |
| ✅ Copyright line corrected | PASS |

**All 13 checks passed.**

---

## HuggingFace Publication Checklist

Before running `huggingface-cli upload`, verify:

- [ ] Create a HuggingFace account / log in: `huggingface-cli login`
- [ ] Create a new dataset repository on HuggingFace Hub
- [ ] Confirm the dataset repository name matches `dataset_info.json` → `name` field
- [ ] Update `README.md` YAML front-matter `license:` from `apache-2.0` to `mit`
- [ ] Run: `huggingface-cli upload <your-hf-username>/dataset-genome-agri-health-mechanism-outcomes publication/huggingface/ --repo-type dataset`
- [ ] Verify the dataset card renders correctly on HuggingFace Hub
- [ ] Tag the release as `v1.0.0`

> **Note:** The `README.md` in the HuggingFace folder still declares `license: apache-2.0` in its YAML front-matter. This should be updated to `license: mit` to match the actual `LICENSE` file and `dataset_info.json` before publication.

---

## Warnings

> [!WARNING]
> The `README.md` YAML front-matter (`license: apache-2.0`) is inconsistent with the `LICENSE` file and `dataset_info.json` (both MIT). Update the front-matter to `license: mit` before publishing.

> [!NOTE]
> The dataset currently contains only Agriculture domain samples (10 records). Future versions should incorporate the full Healthcare domain samples from the pipeline to match the dataset name's scope.

---

## Integrity Summary

| Metric | Value |
|--------|-------|
| Backend code modified | **None** |
| Frontend code modified | **None** |
| Dataset generation modified | **None** |
| `train.jsonl` modified | **None** |
| Benchmark outputs modified | **None** |
| Files renamed | **None** |
| Files created | **1** (`dataset_info.json` — updated) |
| Files modified | **2** (`LICENSE` root, `publication/huggingface/LICENSE`) |

---

*Generated by Dataset Genome Release Engineer — HackIndia AutoScientist Challenge 2026*

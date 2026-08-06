# Benchmark Methodology & Results

## Overview

The Dataset Genome benchmark (`v1.0`) is a **200-sample scientific reasoning benchmark** spanning 10 scientific domains and 4 difficulty levels. It is generated, validated, and scored autonomously using the Adaptive Data Engine.

This document describes the benchmark methodology, scoring system, and official v1.0 results.

---

## Benchmark v1.0 — Official Results

**Report ID:** `rpt-bm-3c90bccb`  
**Generated:** 2026-08-03 15:21:09 UTC  
**Validation Status:** ✅ PASSED

### Quality Metrics

| Metric | Score |
|--------|-------|
| **Composite Adaptive Score** | **88.3 / 100** |
| Knowledge Coverage | 100.0% |
| Reasoning Chain Completeness | 100.0% |
| Experiment Design Diversity | 41.5% |
| Failure Mode Diversity | 100.0% |
| Duplicate Samples | 0 |
| Incomplete Reasoning Chains | 0 |

### Domain Distribution (200 samples, perfectly balanced)

| Scientific Domain | Samples | Share |
|------------------|---------|-------|
| Agriculture | 20 | 10.0% |
| Healthcare | 20 | 10.0% |
| Climate Science | 20 | 10.0% |
| Biology | 20 | 10.0% |
| Chemistry | 20 | 10.0% |
| Physics | 20 | 10.0% |
| Mathematics | 20 | 10.0% |
| Finance | 20 | 10.0% |
| HR | 20 | 10.0% |
| Market Analysis | 20 | 10.0% |

### Difficulty Distribution (200 samples, perfectly balanced)

| Difficulty Level | Samples | Share |
|-----------------|---------|-------|
| Easy | 50 | 25.0% |
| Medium | 50 | 25.0% |
| Hard | 50 | 25.0% |
| Expert | 50 | 25.0% |

---

## Benchmark Scoring Methodology

### Composite Adaptive Score

The Adaptive Score is a weighted composite of four quality dimensions:

```
Adaptive Score = 
    (Knowledge Coverage × 0.30) +
    (Reasoning Completeness × 0.30) +
    (Experiment Diversity × 0.20) +
    (Failure Mode Diversity × 0.20)
```

| Component | Weight | v1.0 Score | Contribution |
|-----------|--------|-----------|-------------|
| Knowledge Coverage | 30% | 100.0% | 30.0 |
| Reasoning Completeness | 30% | 100.0% | 30.0 |
| Experiment Diversity | 20% | 41.5% | 8.3 |
| Failure Mode Diversity | 20% | 100.0% | 20.0 |
| **Total** | **100%** | | **88.3 / 100** |

### Knowledge Coverage

Measures what fraction of the required reasoning fields (`observation`, `identified_problem`, `research_gap`, `primary_hypothesis`, `alternative_hypothesis`, `experiment_design`, `scientific_conclusion`) are non-empty across all samples.

**v1.0:** 100.0% — all reasoning fields present in all 200 samples.

### Reasoning Chain Completeness

Validates that each sample forms a coherent reasoning chain:
- `observation` → `identified_problem` → `primary_hypothesis`
- `experiment_design` → `expected_result` → `scientific_conclusion`

**v1.0:** 100.0% — all 200 samples have complete 7-step reasoning chains.

### Experiment Design Diversity

Measures lexical diversity across `experiment_design` fields to detect generic or repeated template responses. Uses normalized edit distance.

**v1.0:** 41.5% — room for improvement in v2.0 through stronger LLM prompting for methodological variety.

### Failure Mode Diversity

Measures diversity across `failure_cases` fields.

**v1.0:** 100.0% — maximum diversity in failure mode scenarios.

---

## Validation Rules

The `BenchmarkValidator` enforces the following before any export:

| Check | Rule | v1.0 Result |
|-------|------|-------------|
| **Field completeness** | All 17 required fields present | ✅ PASS |
| **Domain balance** | Each domain within ±5% of mean | ✅ PASS |
| **Difficulty balance** | Each level within ±5% of mean | ✅ PASS |
| **Duplicate detection** | 0 duplicate records | ✅ PASS (0 found) |
| **Reasoning chain** | All 7 chain fields non-empty | ✅ PASS |
| **Minimum samples** | ≥ 10 samples per domain | ✅ PASS |

---

## Export Formats

The benchmark is exported to 7 simultaneous formats:

| Format | File | Size |
|--------|------|------|
| JSONL | `benchmark_v1.0.jsonl` | 476 KB |
| JSON | `benchmark_v1.0.json` | 548 KB |
| CSV | `benchmark_v1.0.csv` | 217 KB |
| Parquet | `benchmark_v1.0.parquet` | 477 KB |
| HuggingFace | `benchmark_v1.0_hf.json` | 505 KB |
| Diversity Report | `dataset_diversity_report.json` | 5.5 KB |
| Dashboard Data | `benchmark_dashboard_data.json` | 2.4 KB |

---

## Benchmark Version Lineage

| Version | Samples | Adaptive Score | Coverage | Description |
|---------|---------|---------------|----------|-------------|
| v0.9-beta | — | 78.0 | 70.0% | Pre-release baseline (template-only) |
| **v1.0** | **200** | **88.3** | **100.0%** | Official release — LLM-augmented, 10 domains |

---

## Reproducibility

The benchmark is fully reproducible via the manifest file:

```json
// export_benchmark/reproducibility_manifest.json
{
  "git_commit": "<commit-hash>",
  "random_seed": 42,
  "prompt_version": "v1.0",
  "provider": "gemini",
  "llm_model": "gemini-2.0-flash"
}
```

To reproduce:
```bash
python demo.py   # Regenerates benchmark with the same configuration
```

---

*Full benchmark data available in [`export_benchmark/`](../export_benchmark/). Benchmark report: [`benchmark_report.md`](../export_benchmark/benchmark_report.md).*

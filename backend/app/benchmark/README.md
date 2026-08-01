# Official Dataset Genome Benchmark v1.0

The `benchmark` module generates, validates, manages, versions, and exports the **Official Dataset Genome Benchmark v1.0** dataset — a multi-domain, 16-field scientific reasoning benchmark suitable for open-source release, reproducible evaluation, and hackathon submissions.

---

## 10 Supported Domains & 4 Difficulty Levels

### Supported Domains
1. **Agriculture**
2. **Healthcare**
3. **Climate Science**
4. **Biology**
5. **Chemistry**
6. **Physics**
7. **Mathematics**
8. **Finance**
9. **HR**
10. **Market Analysis**

### Difficulty Levels
- `Easy`
- `Medium`
- `Hard`
- `Expert`

---

## 16-Field Scientific Reasoning Schema

Every benchmark sample enforces a complete 16-field scientific schema:

1. `sample_id`: Unique identifier slug (e.g. `bm-agri-med-001-a1b2`)
2. `dataset_id`: Benchmark dataset version identifier (`dataset-genome-benchmark-v1.0`)
3. `domain`: Scientific domain
4. `difficulty`: Problem difficulty level
5. `prompt`: Scientific inquiry prompt
6. `context`: Observational or experimental context
7. `observation`: Empirical phenomenon observation
8. `problem_identification`: Core problem or bottleneck identified
9. `research_gap`: Knowledge gap or unanswered question
10. `primary_hypothesis`: Testable primary scientific hypothesis
11. `alternative_hypothesis`: Alternative mechanism or counter-hypothesis
12. `experiment_design`: Structured protocol (variables, controls, methodology)
13. `evaluation_metrics`: List of quantitative/qualitative metrics
14. `expected_results`: Predicted outcomes if primary hypothesis holds
15. `failure_cases`: Potential failure modes and disproving outcomes
16. `scientific_conclusion`: Deductive scientific synthesis and conclusion

---

## Component Architecture

```text
benchmark/
├── __init__.py        # Package exports (DatasetGenomeBenchmarkManager, BenchmarkGenerator, etc.)
├── generator.py       # Domain-specific generator synthesizing 16-field scientific samples
├── validator.py       # Validation engine checking duplicates, chain completeness, & balance
├── manager.py         # Master coordinator managing generation, validation, & exports
├── statistics.py      # Statistics engine computing coverage, diversity, & adaptive score
├── exporter.py        # Multi-format exporter (JSON, JSONL, CSV, Parquet, Hugging Face)
├── versioning.py      # Version manager tracking v1.0, v1.1, & v2.0 release lineage
├── models.py          # Pydantic v2 schemas & BenchmarkSampleBuilder
├── report.py          # Exporters for benchmark_report.json and benchmark_report.md
└── README.md          # Official documentation & usage guide
```

---

## Supported Export Formats

- `JSON`: Formatted JSON array (`benchmark_v1.0.json`).
- `JSONL`: Line-delimited JSON (`benchmark_v1.0.jsonl`).
- `CSV`: Tabular CSV spreadsheet (`benchmark_v1.0.csv`).
- `Parquet`: Apache Parquet binary format (`benchmark_v1.0.parquet`).
- `Hugging Face Dataset`: DatasetDict-compatible JSON payload (`benchmark_v1.0_hf.json`).

---

## Usage Example

```python
from app.benchmark import (
    DatasetGenomeBenchmarkManager,
    export_benchmark_report_json,
    export_benchmark_report_markdown,
)

# 1. Instantiate Official Benchmark Manager
manager = DatasetGenomeBenchmarkManager()

# 2. Build Official Benchmark v1.0 Suite
samples, report = manager.build_official_benchmark(
    samples_per_domain=4,  # 40 total samples across 10 domains
    version_tag="v1.0",
    export_dir="publication/benchmark/v1.0",
)

print("Official Benchmark Version:", report.version)
print("Total Generated Samples:", report.statistics.total_samples)
print("Validation Status:", "PASSED" if report.validation.is_valid else "FAILED")
print("Benchmark Adaptive Score:", report.statistics.adaptive_score)

# 3. Export Reports
export_benchmark_report_json(report, output_path="publication/reports/benchmark_report.json")
export_benchmark_report_markdown(report, output_path="publication/reports/benchmark_report.md")
```

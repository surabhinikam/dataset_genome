# Dataset Schema & Methodology

## Overview

The Dataset Genome benchmark uses a structured **10-field scientific reasoning schema** designed to train AI models on complete hypothesis-driven scientific workflows — from initial observation to experimental conclusion.

Each record represents one complete **scientific reasoning chain**, covering problem identification, hypothesis generation, experimental design, expected outcomes, and failure analysis.

---

## Full Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `string` | ✅ | Unique record identifier (format: `rec-{domain}-{idx}-{hex}`) |
| `domain` | `string` | ✅ | Scientific domain (Agriculture, Healthcare, Biology, etc.) |
| `difficulty` | `string` | ✅ | One of: `easy`, `medium`, `hard`, `expert` |
| `prompt` | `string` | ✅ | The full reasoning challenge prompt |
| `context` | `string` | ✅ | Experimental background and data source context |
| `observation` | `string` | ✅ | The anomaly, measurement, or phenomenon to be explained |
| `identified_problem` | `string` | ✅ | Root cause identification statement |
| `research_gap` | `string` | ✅ | Gap in existing scientific literature |
| `primary_hypothesis` | `string` | ✅ | Main testable hypothesis |
| `alternative_hypothesis` | `string` | ✅ | Competing alternative explanation |
| `experiment_design` | `string` | ✅ | Proposed experimental methodology |
| `control_variables` | `list[string]` | ✅ | Variables held constant in the experiment |
| `evaluation_metrics` | `list[string]` | ✅ | Measurable outcome metrics |
| `expected_result` | `string` | ✅ | Predicted experimental outcome |
| `failure_cases` | `list[string]` | ✅ | Known failure modes and edge cases |
| `scientific_conclusion` | `string` | ✅ | Conclusion drawn if primary hypothesis is supported |
| `created_at` | `string` | ✅ | ISO 8601 generation timestamp |

---

## Sample Record (Agriculture Domain)

```json
{
  "id": "rec-agriculture-001-44863d",
  "domain": "Agriculture",
  "difficulty": "hard",
  "prompt": "Evaluate scientific dataset anomaly in Agriculture (Sample #1): Unexpected 14% drop in crop yield despite optimal nitrogen fertilizer application. Formulate primary hypothesis and experimental validation design.",
  "context": "Soil moisture and crop yield telemetry collected across 500 agricultural test plots.",
  "observation": "Unexpected 14% drop in crop yield despite optimal nitrogen fertilizer application. (Trial Iteration #1)",
  "identified_problem": "Micro-nutrient imbalance (Zinc deficiency) inhibiting nitrogen absorption.",
  "research_gap": "Lack of real-time multi-spectral soil mineral interaction modeling.",
  "primary_hypothesis": "Foliar application of chelated zinc will restore nitrogen uptake and increase yield by >= 10%.",
  "alternative_hypothesis": "Soil compaction is restricting root growth independently of mineral availability.",
  "experiment_design": "Split-plot randomized control trial applying 2.5 kg/ha chelated zinc vs baseline control.",
  "control_variables": [
    "Nitrogen application rate",
    "Irrigation volume",
    "Solar radiation"
  ],
  "evaluation_metrics": [
    "yield_per_hectare",
    "leaf_zinc_concentration",
    "nitrogen_use_efficiency"
  ],
  "expected_result": "Leaf zinc concentration increases above 25 ppm, boosting crop yield by 12%.",
  "failure_cases": [
    "Heavy rainfall leaching foliar spray",
    "Soil pH below 5.5 locking zinc availability"
  ],
  "scientific_conclusion": "Zinc supplementation resolves micronutrient bottleneck and maximizes nitrogen fertilizer efficiency.",
  "created_at": "2026-08-03 15:22:00.677069"
}
```

---

## Generation Methodology

### 1. Template-Based Seeding

Each domain has a base template (`backend/app/dataset_generator/templates.py`) that provides:
- A canonical `observation` scenario with real scientific grounding
- Initial `context`, `identified_problem`, and `research_gap`
- A validated `experiment_design` structure

### 2. LLM-Augmented Generation

The `LLMBenchmarkGenerator` (`backend/app/benchmark/llm_generator.py`) uses the `BenchmarkPromptBuilder` to construct structured prompts, then calls a configured LLM provider (Gemini, OpenAI, or Anthropic) to generate scientifically diverse completions.

**Generation parameters:**
- Base temperature: `0.85`
- Temperature nudge per retry: `+0.05`
- Max temperature cap: `1.20`
- Max retries per slot: `3`
- Uniqueness hint: index-offset on retry

### 3. Reasoning Style Diversity

Each sample is tagged with one of **7 reasoning styles** to ensure epistemic diversity:

| Style | Description |
|-------|-------------|
| Positive Result | Hypothesis is supported by experiment |
| Negative Result | Hypothesis is disproved |
| Ambiguous Result | Evidence is inconclusive |
| Conflicting Literature | Results contradict prior studies |
| Failed Experiment | Trial is invalidated by measurement failure |
| Replication Study | Reproducing an existing landmark study |
| Unexpected Observation | Anomalous secondary effect discovered |

### 4. Validation & Quality Scoring

After generation, each sample passes through:

1. **`BenchmarkValidator`** — checks field completeness, reasoning chain integrity, and domain/difficulty balance
2. **`BenchmarkDeduplicator`** — detects near-duplicate samples via hash comparison
3. **`BenchmarkQualityScorer`** — attaches per-sample and suite-level quality scores

### 5. Export

Validated samples are exported simultaneously to:
- `JSONL` — primary training format
- `JSON` — structured archive
- `CSV` — tabular analysis
- `Parquet` — columnar storage (via `pyarrow`)
- `HuggingFace` — dataset card + upload-ready package

---

## Dataset Versions

| Version | Samples | Domains | Adaptive Score | Release Date |
|---------|---------|---------|----------------|--------------|
| v1.0 (HF Release) | 20 | Agriculture | — | 2026-08-06 |
| v1.0 (Full Benchmark) | 200 | 10 | 88.3/100 | 2026-08-03 |

---

## Field Length Constraints

| Field | Approx. Length |
|-------|---------------|
| `prompt` | 200–400 characters |
| `context` | 80–200 characters |
| `observation` | 100–250 characters |
| `primary_hypothesis` | 100–300 characters |
| `experiment_design` | 100–300 characters |
| `scientific_conclusion` | 80–250 characters |
| `control_variables` | 2–5 items |
| `evaluation_metrics` | 2–5 items |
| `failure_cases` | 2–4 items |

---

## Supported Domains

| Domain | Template Scenarios |
|--------|--------------------|
| Agriculture | Crop yield anomalies, soil mineral imbalances, irrigation failures |
| Healthcare | Drug response anomalies, clinical trial outcomes, biomarker shifts |
| Climate Science | Atmospheric CO₂ anomalies, temperature feedback loops |
| Biology | Cellular mechanism failures, gene expression anomalies |
| Chemistry | Reaction yield deficits, catalyst poisoning |
| Physics | Quantum decoherence events, material property anomalies |
| Mathematics | Convergence failures, numerical stability issues |
| Finance | Market anomaly detection, risk model failures |
| HR | Workforce productivity anomalies, attrition predictors |
| Market Analysis | Demand forecasting errors, supply chain disruptions |

---

*See [`benchmark.md`](benchmark.md) for quality metrics and [`training.md`](training.md) for how this dataset is used in AutoScientist training.*

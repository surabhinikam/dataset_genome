# Dataset Generator — Dataset Genome Scientific Reasoning Benchmark

The `dataset_generator` module provides an extensible framework for generating, formatting, and exporting scientific reasoning benchmark datasets for Dataset Genome.

---

## Directory Structure

```text
dataset_generator/
│
├── __init__.py      # Module exports
├── generator.py     # Core DatasetGenerator coordinator class
├── models.py        # Pydantic v2 domain schemas (ScientificReasoningRecord)
├── templates.py     # Domain seeds and scientific reasoning prompt templates
├── exporters.py     # JSONL dataset file exporter
└── README.md        # Documentation and usage guide
```

---

## Data Model: `ScientificReasoningRecord`

All generated records conform to the 16-field Pydantic v2 schema:

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Unique record slug (e.g. `rec-agriculture-001-a1b2c3`) |
| `domain` | `str` | Scientific domain (e.g. `Agriculture`, `Medicine`, `Climate Science`) |
| `difficulty` | `str` | Problem difficulty (`easy`, `medium`, `hard`) |
| `prompt` | `str` | User benchmark prompt statement |
| `context` | `str` | Background scientific context and telemetry baseline |
| `observation` | `str` | Empirical scientific observation or anomaly |
| `identified_problem` | `str` | Underlying data or physical mechanism flaw |
| `research_gap` | `str` | Unresolved research gap |
| `primary_hypothesis` | `str` | Primary testable hypothesis statement |
| `alternative_hypothesis` | `str` | Alternative counter hypothesis statement |
| `experiment_design` | `str` | Controlled experimental setup and procedure |
| `control_variables` | `List[str]` | List of control variables held constant |
| `evaluation_metrics` | `List[str]` | Quantitative target evaluation metrics |
| `expected_result` | `str` | Anticipated quantitative and qualitative result |
| `failure_cases` | `List[str]` | Potential failure modes or edge cases |
| `scientific_conclusion` | `str` | Synthesized scientific conclusion |

---

## Usage Examples

### 1. In-Memory Generation

```python
from backend.app.dataset_generator import DatasetGenerator

generator = DatasetGenerator()
records = generator.generate("Agriculture", 20)

print(f"Generated {len(records)} records for domain '{records[0].domain}'")
print("First Record ID:", records[0].id)
```

### 2. Generating and Exporting directly to JSONL

```python
from backend.app.dataset_generator import DatasetGenerator

generator = DatasetGenerator()

# Exports to datasets/raw/scientific_reasoning_v1.jsonl by default
result = generator.generate_and_export(domain="Agriculture", count=20)

print(f"Exported {result.total_records} records to '{result.output_path}'")
```

---

## Supported Output Format

Results are exported as JSON Lines (`.jsonl`) files where each line is a valid Pydantic v2 JSON string:

```json
{"id":"rec-agriculture-001-f1a2b3","domain":"Agriculture","difficulty":"medium","prompt":"...","context":"...","observation":"...","identified_problem":"...","research_gap":"...","primary_hypothesis":"...","alternative_hypothesis":"...","experiment_design":"...","control_variables":["Nitrogen application rate"],"evaluation_metrics":["yield_per_hectare"],"expected_result":"...","failure_cases":["Heavy rainfall"],"scientific_conclusion":"..."}
```

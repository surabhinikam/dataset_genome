# Research Gap — Dataset Genome

## Overview

This document identifies the key research and engineering gaps that Dataset
Genome is designed to address, situating the project within the broader
landscape of data management, machine learning, and AI research.

---

## 1. The Missing Dataset Fingerprint Standard

**Gap**: There is no widely adopted, machine-readable standard for describing
the *intrinsic properties* of a tabular dataset.

**Current State**:
- Hugging Face Dataset Cards are Markdown files — human-readable but not
  structured or machine-parsable.
- Data dictionaries are manually maintained and quickly go stale.
- OpenML provides metadata for benchmark datasets, but not for arbitrary
  user uploads.
- `pandas-profiling` / `ydata-profiling` generates rich HTML reports, but
  output is not a standardised schema.

**Dataset Genome Contribution**: Define and implement a structured,
JSON-serialisable schema for dataset metadata that covers structure,
statistics, semantics, and lineage.

---

## 2. LLM-Assisted Data Understanding

**Gap**: LLMs are routinely used to write code and summarise text, but their
application to *understanding tabular data schemas* at scale is underexplored.

**Research Questions**:
- How accurately can an LLM infer column semantics (e.g., "this is a currency
  column") from a column name + sample values alone?
- What prompt strategies yield the most consistent column descriptions across
  diverse domains?
- Can an LLM reliably classify a dataset's domain (finance, healthcare,
  geospatial) from structural features?

**Relevant Prior Work**:
- *PASTA* (VLDB 2023) — table understanding via language models
- *TableGPT* (2023) — GPT for tabular data question-answering
- *DITTO* (SIGMOD 2021) — entity matching with transformers

**Dataset Genome Contribution**: Systematic evaluation of LLM-based column
annotation quality across multiple domains and dataset sizes.

---

## 3. Dataset Similarity and Transferability

**Gap**: Given two datasets, there is no principled, lightweight method to
estimate whether knowledge (features, model weights) from one transfers to
the other — without training a model first.

**Research Questions**:
- Can dataset Genome vectors (embeddings of the dataset fingerprint) be used
  to predict transfer learning success?
- How do structural similarity and semantic similarity differ in predicting
  model performance?

**Relevant Prior Work**:
- *H-Score* (ICML 2019) — transferability estimation
- *LogME* (ICML 2021) — label-data compatibility
- *Dataset2Vec* (2019) — learning dataset embeddings for meta-learning

**Dataset Genome Contribution**: A vector representation of the full dataset
Genome (structural + statistical + semantic) for similarity search and
transferability prediction.

---

## 4. Automated Data Quality Assessment

**Gap**: Data quality assessment tools exist (Great Expectations, Soda Core)
but require manual rule authoring — they do not *learn* what quality means for
a given dataset type.

**Research Questions**:
- Can quality heuristics be learned from historical data quality labels?
- Can an LLM propose domain-appropriate quality checks given a dataset schema?

**Dataset Genome Contribution**: An AI-generated quality assessment pipeline
that adapts to dataset domain and structure.

---

## 5. Reproducibility and Dataset Provenance

**Gap**: ML reproducibility is hampered by the absence of a standardised,
version-controlled dataset identity. The same CSV file may be modified silently,
breaking experiment reproducibility.

**Research Questions**:
- What minimal metadata is required to uniquely and reproducibly identify a
  dataset version?
- How can Genome versioning integrate with existing MLOps tooling (DVC, MLflow)?

**Dataset Genome Contribution**: A versioned Genome schema with a content hash
(SHA-256 of the file) as part of the dataset fingerprint.

---

## 6. Related Work Summary

| Tool / Paper | Overlap | Gap Addressed |
|---|---|---|
| Hugging Face Dataset Cards | Human-readable dataset descriptions | Not machine-parsable; no statistical layer |
| ydata-profiling | Statistical profiling | No semantic layer; not an API service |
| OpenML | Benchmark dataset metadata | Limited to pre-curated datasets; no LLM layer |
| Dataset2Vec | Dataset embeddings | No semantic annotation; no user-facing API |
| PASTA / TableGPT | LLM + tabular data | Not a dataset fingerprint standard |
| Great Expectations | Data quality | Requires manual rule authoring |

---

## Conclusion

Dataset Genome occupies a unique niche: it combines **structural metadata
extraction**, **AI-powered semantic annotation**, **quality assessment**, and
**vector-based similarity search** into a single, open, API-first platform.
No existing tool addresses all four dimensions simultaneously with a
user-friendly interface. This is the research and engineering gap we intend
to close.

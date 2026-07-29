# Vision — Dataset Genome

## What Is Dataset Genome?

Dataset Genome is an AI-powered research platform designed to make datasets
*self-describing*. Just as a biological genome encodes the complete blueprint
of an organism, a Dataset Genome encodes the structural, statistical, and
semantic blueprint of a data file — enabling machines and researchers to
understand datasets at a glance.

## Problem Statement

Data scientists spend an estimated **60–80 % of their time on data wrangling**
(Forbes, 2016). A significant portion of this time is consumed by the simple
task of *understanding* a dataset before any analysis begins:

- What columns does it have?
- What are the data types?
- Are there missing values?
- What is the statistical distribution of each feature?
- Is this dataset suitable for a given ML task?

These questions are currently answered manually — opening files in Excel,
running `df.describe()` in Jupyter, reading README files that are often
outdated. There is no standardised, machine-readable *fingerprint* for a
dataset.

## Our Vision

We envision a future where every dataset ships with a **Genome** — a
structured, versioned, AI-generated document that describes:

| Layer | Contents |
|-------|----------|
| **Structure** | Schema, column names, types, row/column counts |
| **Statistics** | Distributions, outliers, correlations, missing-value rates |
| **Semantics** | Natural-language column descriptions, domain classification |
| **Lineage** | Provenance, transformations, versioning history |
| **Fitness** | Suitability scores for common ML tasks |

## Why Now?

Large language models have reached the capability threshold required to
generate rich semantic descriptions of tabular data reliably. Combined with
open-source pandas-compatible tooling and vector databases for similarity
search, the infrastructure to build Dataset Genome is mature and available
today.

## Target Users

- **ML Engineers** who need to evaluate datasets quickly before committing to
  preprocessing pipelines.
- **Research Scientists** who want reproducible, citable dataset descriptions.
- **Data Cataloguers** who maintain large repositories of datasets and need
  automated metadata generation.
- **Educators** who want to find datasets suitable for teaching specific
  concepts.

## Sprint 1 Scope

Sprint 1 delivers the foundation: a working full-stack application that
accepts a CSV file and returns its structural metadata. No AI logic yet —
just clean architecture ready to receive it in Sprint 2.

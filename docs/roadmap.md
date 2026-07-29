# Roadmap — Dataset Genome

> Iterative sprints from MVP foundation to full AI-powered dataset intelligence.

---

## ✅ Sprint 1 — Foundation (Current)

**Goal**: Build a working full-stack monorepo with clean architecture.

| Feature | Status |
|---------|--------|
| FastAPI backend with modular architecture | ✅ Done |
| Health endpoint (`GET /health`) | ✅ Done |
| CSV upload endpoint (`POST /upload`) | ✅ Done |
| File validation (type + MIME) | ✅ Done |
| Pandas-based metadata extraction | ✅ Done |
| Next.js 15 dashboard frontend | ✅ Done |
| Drag-and-drop CSV upload UI | ✅ Done |
| Metadata display panel | ✅ Done |
| CORS configuration | ✅ Done |
| Project documentation | ✅ Done |

---

## 🔜 Sprint 2 — Data Persistence & Statistics

**Goal**: Persist datasets and compute rich statistical metadata.

- [ ] PostgreSQL database with SQLAlchemy ORM
- [ ] Alembic migrations
- [ ] Dataset history — list all uploaded datasets (`GET /datasets`)
- [ ] Individual dataset retrieval (`GET /datasets/{id}`)
- [ ] Statistical analysis per column:
  - Data type inference (numeric, categorical, datetime, text)
  - Min / max / mean / median / std dev
  - Null value counts and percentages
  - Unique value counts
  - Top-N most frequent values (categorical)
- [ ] Frontend dataset history table
- [ ] Statistical charts (histogram, bar chart) via Recharts

---

## 🔜 Sprint 3 — AI Semantic Layer

**Goal**: Use LLMs to generate natural-language descriptions of datasets.

- [ ] Column semantic annotation via OpenAI / Gemini API
- [ ] Dataset-level description generation
- [ ] Domain classification (finance, healthcare, e-commerce, etc.)
- [ ] ML task fitness scoring (classification, regression, clustering suitability)
- [ ] Structured Genome JSON output (exportable)
- [ ] Background processing queue (Celery + Redis)
- [ ] Progress indicator on frontend

---

## 🔜 Sprint 4 — Search & Discovery

**Goal**: Make datasets discoverable via semantic similarity.

- [ ] Vector embeddings for dataset Genomes (OpenAI embeddings or sentence-transformers)
- [ ] pgvector or Chroma for similarity search
- [ ] `POST /datasets/search` — find similar datasets
- [ ] `GET /datasets?query=...` — semantic search over all uploaded datasets
- [ ] Frontend search bar with instant results

---

## 🔜 Sprint 5 — Authentication & Multi-tenancy

**Goal**: Support multiple users with isolated dataset workspaces.

- [ ] JWT-based authentication (register, login, refresh)
- [ ] User-scoped dataset storage
- [ ] API key support for programmatic access
- [ ] Rate limiting per user

---

## 🔜 Sprint 6 — Dataset Quality & Recommendations

**Goal**: Identify data quality issues and recommend fixes.

- [ ] Missing value detection and imputation suggestions
- [ ] Outlier detection (IQR, Z-score)
- [ ] Duplicate row detection
- [ ] Schema drift detection (compare two dataset versions)
- [ ] Preprocessing recommendations
- [ ] Quality score (0–100) per dataset

---

## 🔜 Sprint 7 — Export & Integrations

**Goal**: Make Dataset Genome usable in existing workflows.

- [ ] Export Genome as JSON, YAML, or Markdown
- [ ] GitHub Action: generate Genome on CSV push
- [ ] Hugging Face Dataset Card generator
- [ ] Python SDK (`dataset-genome` package on PyPI)
- [ ] REST API documentation site (Mintlify / Docusaurus)

---

## Long-term Vision

By Sprint 7, Dataset Genome will be a comprehensive open-source platform
enabling any data practitioner to generate rich, AI-annotated, machine-readable
fingerprints for their datasets — making data discovery, reuse, and
reproducibility dramatically easier.

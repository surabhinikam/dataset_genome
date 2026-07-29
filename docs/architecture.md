# Architecture — Dataset Genome

## System Overview

Dataset Genome is a **monorepo** containing two independent applications:
a React/Next.js frontend and a Python/FastAPI backend. They communicate
exclusively via a typed REST API.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Browser                           │
│                     (localhost:3000)                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Next.js 15  (App Router)                    │  │
│  │                                                           │  │
│  │  ┌─────────────────┐   ┌────────────────────────────┐   │  │
│  │  │  CsvUpload      │   │  DatasetMetadataPanel      │   │  │
│  │  │  Component      │──▶│  Component                 │   │  │
│  │  └─────────────────┘   └────────────────────────────┘   │  │
│  │         │                                                 │  │
│  │   lib/api.ts  (typed HTTP client)                        │  │
│  └──────────────────────│────────────────────────────────────┘  │
└─────────────────────────│────────────────────────────────────────┘
                          │ HTTP (multipart/form-data & JSON)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI  (localhost:8000)                      │
│                                                                 │
│  ┌───────────┐   ┌──────────────────────┐   ┌───────────────┐  │
│  │  /health  │   │  /upload             │   │  CORS         │  │
│  │  route    │   │  route               │   │  Middleware   │  │
│  └───────────┘   └──────────────────────┘   └───────────────┘  │
│                          │                                       │
│                  ┌───────┴──────────┐                           │
│                  │  utils/          │                            │
│                  │  file_utils.py   │                            │
│                  │  (validation,    │                            │
│                  │   storage)       │                            │
│                  └───────┬──────────┘                           │
│                          │                                       │
│                  ┌───────┴──────────┐                           │
│                  │  services/       │                            │
│                  │  csv_processor   │                            │
│                  │  (pandas)        │                            │
│                  └───────┬──────────┘                           │
│                          │                                       │
│                  ┌───────┴──────────┐                           │
│                  │  uploads/        │                            │
│                  │  (filesystem)    │                            │
│                  └──────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backend Architecture

The backend follows **Clean Architecture** with clear layer separation:

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| API | `api/routes/` | HTTP request/response handling |
| Services | `services/` | Business logic (CSV processing) |
| Schemas | `schemas/` | Pydantic request/response models |
| Utils | `utils/` | Shared helpers (file I/O, validation) |
| Core | `core/` | Configuration, constants |

### SOLID Principles Applied

- **Single Responsibility**: Each module has one job (e.g., `csv_processor.py`
  only processes CSVs; `file_utils.py` only manages file I/O).
- **Open/Closed**: Adding a new file format (e.g., Parquet) means adding a new
  service, not modifying the upload route.
- **Liskov Substitution**: Service functions accept typed parameters and are
  replaceable with mocks in tests.
- **Interface Segregation**: Pydantic schemas expose only the fields needed at
  each API boundary.
- **Dependency Inversion**: The upload route depends on the service abstraction,
  not concrete pandas calls.

### Request Flow

```
POST /upload
  │
  ├─ 1. validate_csv_file()     → HTTP 400 if invalid extension/MIME
  ├─ 2. generate_upload_path()  → UUID + safe filename
  ├─ 3. save_upload_file()      → Stream to disk (chunked, 64 KB)
  └─ 4. process_csv()           → pandas metadata extraction
        └─ Return DatasetMetadataResponse (JSON)
```

---

## Frontend Architecture

The frontend uses **Next.js 15 App Router** with a component-first structure:

| File | Role |
|------|------|
| `app/page.tsx` | Dashboard page (layout, state orchestration) |
| `app/layout.tsx` | Root shell (fonts, metadata) |
| `components/header.tsx` | Navigation bar + API status badge |
| `components/csv-upload.tsx` | File input + drag-and-drop + upload logic |
| `components/dataset-metadata.tsx` | Metadata display panel |
| `lib/api.ts` | Typed HTTP client (all fetch calls centralised) |
| `types/dataset.ts` | TypeScript interfaces mirroring backend schemas |

### Data Flow

```
user selects file
  → CsvUpload validates (client-side extension check)
  → uploadCSV() in lib/api.ts sends multipart POST
  → backend returns DatasetMetadata JSON
  → page.tsx stores metadata in useState
  → DatasetMetadataPanel renders the results
```

---

## Data Storage (Sprint 1)

Uploaded files are persisted to the local filesystem under `backend/uploads/`.
Files are named `{uuid}_{original_filename}` to prevent collisions. No database
is used in Sprint 1 — metadata is computed on-the-fly and returned in the
HTTP response.

**Sprint 2+ Plan**: Introduce PostgreSQL + SQLAlchemy for persistent dataset
records, enabling history, search, and versioning.

---

## Security Considerations (Sprint 1)

| Concern | Mitigation |
|---------|-----------|
| File type spoofing | Both extension AND MIME type checked |
| Large file uploads | 50 MB hard limit with chunked streaming |
| Path traversal | UUID prefix + `pathlib.Path` for safe joining |
| CORS | Explicit allow-list (localhost:3000 only) |

---

## Future Architecture (Sprint 2+)

- **Database**: PostgreSQL via SQLAlchemy + Alembic migrations
- **AI Layer**: LLM-powered column semantic annotation
- **Queue**: Celery + Redis for async heavy analysis
- **Auth**: JWT-based authentication
- **Search**: Vector similarity search for dataset discovery

<<<<<<< HEAD
# Dataset Genome

> **Sprint 1 — Foundation** · AI-powered dataset intelligence platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)](https://typescriptlang.org)

---

## 📁 Project Structure

```
dataset_genome/
├── backend/               # FastAPI Python API
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py  # GET /health
│   │   │   └── upload.py  # POST /upload
│   │   └── router.py
│   ├── core/
│   │   └── config.py      # Pydantic settings
│   ├── schemas/
│   │   └── dataset.py     # Response models
│   ├── services/
│   │   └── csv_processor.py
│   ├── utils/
│   │   └── file_utils.py
│   ├── uploads/           # Saved CSV files (git-ignored)
│   ├── main.py            # Entry point
│   └── requirements.txt
├── frontend/              # Next.js 15 app
│   └── src/
│       ├── app/           # App Router pages
│       ├── components/    # UI components
│       ├── lib/           # API client
│       └── types/         # TypeScript interfaces
├── docs/                  # Project documentation
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── research-gap.md
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Node.js | 18+ |
| npm | 9+ |

---

### Backend Setup

> **Windows Note**: If you installed Python via MSYS2/pacman, use `py -3.11` or point to your python.org Python installation (`C:\Python311\python.exe`). MSYS2 Python lacks binary wheels for packages like `pydantic-core` and `pandas`.

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
# Windows (python.org install - recommended)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

The dashboard will be available at **http://localhost:3000**

---

### Optional — Environment Variables

Create `frontend/.env.local` to override the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📡 API Reference

### `GET /health`

Returns the API status and version.

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### `POST /upload`

Upload a CSV file for analysis.

**Request:** `multipart/form-data` with a `file` field containing a `.csv` file.

**Response:**

```json
{
  "dataset_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "filename": "iris.csv",
  "num_rows": 150,
  "num_cols": 5,
  "column_names": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
}
```

**Error Responses:**

| Code | Meaning |
|------|---------|
| 400 | Invalid file type or missing filename |
| 413 | File exceeds 50 MB limit |
| 422 | CSV is empty or cannot be parsed |
| 500 | Unexpected server error |

---

## 🧪 Testing the Upload

```bash
# Using curl
curl -X POST http://localhost:8000/upload \
  -F "file=@/path/to/your/dataset.csv"
```

---

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for the full technical overview.

---

## 🗺️ Roadmap

See [docs/roadmap.md](docs/roadmap.md) for planned sprints and features.

---

## 🔬 Research Vision

See [docs/vision.md](docs/vision.md) and [docs/research-gap.md](docs/research-gap.md) for the research motivation behind this project.

---

## 📝 License

MIT © Dataset Genome Team
=======
# adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes
Hackathon team repository for surabhi_codes - [hackindia-team:adaption-autoscientist-challenge-part-2-60000-prize-pool:surabhicodes]
>>>>>>> 6b5edac30675a5e543bec213c29f79fde0083c1a

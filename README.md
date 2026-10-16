# MGSE — Macro Grocery Search Engine

Australian meal generator: hybrid retrieval (MongoDB filters + local embeddings) → Gemini structured draft → scipy gram optimiser → FastAPI + React UI.

Generates **one meal per request** against NRAUS prices and AUSNUT 2023 nutrition.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for the frontend)
- **MongoDB** running locally on `mongodb://localhost:27017/`
- A **Gemini API key** ([Google AI Studio](https://aistudio.google.com/apikey))

---

## 1. Clone and enter the project

```powershell
cd C:\Users\joshu\OneDrive\Desktop\Joshua\cs\etl
```

(Or clone your GitHub repo and `cd` into it.)

---

## 2. Create a Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn pymongo sentence-transformers scipy pydantic python-dotenv google-genai openpyxl pandas numpy
```

Keep this venv activated for all Python commands below.

---

## 3. Configure `.env`

Create a `.env` file in the project root (same folder as `api.py`):

```env
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.5-flash-lite
```

`.env` is gitignored

If `gemini-3.5-flash-lite` is busy or unavailable, try another model from the Gemini docs (e.g. `gemini-flash-lite-latest`).

---

## 4. Load data into MongoDB (first time, or after dataset changes)

Datasets live in `datasets/`. Close any Excel files that have them open, then:

```powershell
python ingestion.py
python embed.py
```

- `ingestion.py` — joins NRAUS prices with AUSNUT nutrients, upserts into `nutrition_db.products`
- `embed.py` — writes `all-MiniLM-L6-v2` embeddings onto each product (required after every ingestion, because ingestion replaces documents)

Expect on the order of **~376** products with embeddings.

Quick check:

```powershell
python -c "from pymongo import MongoClient; c=MongoClient()['nutrition_db']['products']; print(c.count_documents({'embedding': {'$exists': True}}))"
```

---

## 5. Start the API

```powershell
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see `Application startup complete` (the embedding model can take a few seconds on first load).

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/docs | Interactive API docs |
| http://127.0.0.1:8000/health | MongoDB + Gemini key readiness |

---

## 6. Start the frontend

New terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually **http://127.0.0.1:5173**).

The UI talks to `http://127.0.0.1:8000` (override with `VITE_API_URL` if needed).

---

## Everyday run (after setup)

**Terminal 1 — API**

```powershell
cd C:\Users\joshu\OneDrive\Desktop\Joshua\cs\etl
.\venv\Scripts\Activate.ps1
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — UI**

```powershell
cd C:\Users\joshu\OneDrive\Desktop\Joshua\cs\etl\frontend
npm run dev
```

MongoDB must already be running.

---

## Optional: evaluation harness (CV metrics)

With the API dependencies available (MongoDB + `.env`), from the project root:

```powershell
python evaluate.py
```

Runs ~30 fixed meal requests and writes `eval_results.csv` plus a console summary (valid first-draft rate, feasibility, retries, latency). This calls Gemini many times and can take several minutes.

---

## Optional: smoke-test pieces

```powershell
python retrieval.py          # hybrid search demos
python planner.py            # one dinner end-to-end
python playground_meal.py    # Pydantic + optimiser only (no LLM)
```

---

## Project layout (main files)

| Path | Role |
|------|------|
| `ingestion.py` | ETL → MongoDB |
| `embed.py` | Sentence-transformer embeddings |
| `retrieval.py` | Hybrid search |
| `models.py` | Pydantic request/response schemas |
| `optimizer.py` | `scipy.optimize.linprog` portion sizes |
| `llm.py` | Gemini structured `MealDraft` |
| `planner.py` | Search → draft → validate → optimise |
| `api.py` | FastAPI |
| `evaluate.py` | Batch evaluation |
| `frontend/` | Vite + React + TypeScript UI |
| `datasets/` | NRAUS + AUSNUT Excel sources |

---

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| `API unreachable` on the UI | Start uvicorn; wait for startup to finish; refresh the page |
| `GEMINI_API_KEY is not set` | Add the key to `.env` and restart uvicorn |
| Gemini `503` / high demand | Wait and retry, or change `GEMINI_MODEL` in `.env` |
| Gemini `404` model not found | Use a current model id from the Gemini docs |
| Empty / odd search results | Re-run `ingestion.py` then `embed.py` |
| `openpyxl` / Excel errors | `pip install openpyxl`; close Excel lock files (`~$...`) |
| Frontend CORS errors | API must allow `http://localhost:5173` (already set in `api.py`) |

---

## Notes

- Prices are a **Dec 2020 NRAUS** snapshot (Coles/Woolworths NSW), not live supermarket prices.
- Nutrition is from **AUSNUT 2023**, joined via the official 2011–13 matching file.
- This prototype generates **one meal** per request (not a full day/week plan).

## Future implementation
- Generate more meal plans for a week, more like a comprehensive meal planner.
- Some more Front-end changes.
- Quality of code optimizations.
- Parse realtime data.

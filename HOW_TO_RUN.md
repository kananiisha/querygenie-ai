# QueryGenie AI — How to Run Locally

## Every time you want to run the project, do this:

### Step 1 — Seed the database (only needed once, or if DB is deleted)
```powershell
python seed_sqlite.py
```

### Step 2 — Terminal 1: Start Backend
```powershell
python -m uvicorn backend.main:app --reload
```
Backend runs at: http://127.0.0.1:8000
Test it: http://127.0.0.1:8000/health → should show {"status":"ok"}

### Step 3 — Terminal 2: Start Frontend
```powershell
python -m streamlit run frontend/app.py
```
Frontend runs at: http://localhost:8501

---

## Also index the schema (if qdrant_storage is missing or deleted)
```powershell
python -m backend.schema_indexer.index_schema
```

---

## Quick test the full AI pipeline (no UI needed)
```powershell
python -m backend.agents.pipeline
```

---

## Git — push your changes
```powershell
git add .
git commit -m "your message here"
git push
```

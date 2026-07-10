# 🔍 QueryGenie AI

> Ask your business database anything in plain English — no SQL knowledge needed.

![CI](https://github.com/kananiisha/querygenie-ai/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-green)
![Accuracy](https://img.shields.io/badge/Benchmark_Accuracy-95%25-brightgreen)

---

## 🎯 Problem

Non-technical business teams depend on data analysts for every small data question — slowing down decisions. QueryGenie AI lets anyone query a real database conversationally, with a multi-agent pipeline that validates every generated SQL query before it runs.

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────────────┐
│  Schema Retriever   │  ← Finds relevant tables from Qdrant (RAG)
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│   SQL Generator     │  ← Writes SELECT query using Groq LLaMA 3.3
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│  Validator/Safety   │  ← Blocks unsafe queries, retries with feedback
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│  Query Executor     │  ← Runs validated SQL against real database
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│     Explainer       │  ← Turns raw results into plain-English answer
└─────────────────────┘
      │
      ▼
  Plain-English Answer + SQL + Raw Data
```

---

## 🤖 Agent Pipeline

| Agent | Role |
|---|---|
| **Schema Retriever** | Semantic search over table descriptions using sentence-transformers + Qdrant |
| **SQL Generator** | Generates a SELECT-only query using Groq LLaMA 3.3 70B |
| **Validator** | Blocks DROP/DELETE/UPDATE/multi-statement queries, retries with feedback |
| **Executor** | Runs the validated SQL against the database (read-only) |
| **Explainer** | Converts raw results into a plain-English answer |

---

## 📊 Benchmark Results

Evaluated on a **20-question golden test set**:

| Category | Score |
|---|---|
| Count queries | 11/11 (100%) |
| Aggregation queries | 1/1 (100%) |
| Filter queries | 7/8 (88%) |
| **Overall** | **19/20 (95%)** |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq LLaMA 3.3 70B |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | Qdrant |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Streamlit |
| CI/CD | GitHub Actions |

---

## 👥 Team

| Member | Role |
|---|---|
| **Isha Kanani** | AI Module — schema embeddings, agent pipeline, accuracy benchmark |
| **Mokshi** | Backend (FastAPI, auth, DB) + Frontend (Streamlit UI) |

---

## 🚀 Setup & Run

```bash
# Clone
git clone https://github.com/kananiisha/querygenie-ai.git
cd querygenie-ai

# Install
cd backend && python -m pip install -r requirements.txt && cd ..

# Create backend/.env
# DATABASE_URL=sqlite:///./querygenie_dev.db
# GROQ_API_KEY=your_key
# SECRET_KEY=your_secret

# Seed DB (once)
python seed_sqlite.py

# Index schema (once)
python -m backend.schema_indexer.index_schema

# Terminal 1 - Backend
python -m uvicorn backend.main:app --reload

# Terminal 2 - Frontend
python -m streamlit run frontend/app.py
```

Open **http://localhost:8501**

### Run Benchmark
```bash
python benchmark.py
```

---

## 📁 Project Structure

```
querygenie-ai/
├── backend/
│   ├── agents/
│   │   ├── sql_generator.py
│   │   ├── validator.py
│   │   ├── executor.py
│   │   ├── explainer.py
│   │   └── pipeline.py
│   ├── schema_indexer/
│   │   ├── schema_metadata.py
│   │   ├── index_schema.py
│   │   └── retrieve_schema.py
│   ├── main.py
│   ├── database.py
│   ├── auth.py
│   └── requirements.txt
├── frontend/
│   └── app.py
├── tests/
├── benchmark.py
├── seed_sqlite.py
└── README.md
```

---

## 🔒 Security

- Read-only database connection — executor cannot write/delete
- Validator blocks DROP, DELETE, UPDATE, ALTER, multi-statement queries
- Prompt injection protection
- JWT authentication on protected endpoints
- Full audit log of every query

---

## 📄 License

MIT License

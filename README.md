# QueryGenie AI
![CI](https://github.com/kananiisha/querygenie-ai/actions/workflows/ci.yml/badge.svg)

Ask your business database questions in plain English — safely.

## Problem
Non-technical teams depend on a data analyst for every small data question. QueryGenie lets anyone query a real database conversationally, with a multi-agent pipeline that validates every generated SQL query before it runs.

## Team
- **Isha** — AI module (schema embeddings, agent pipeline, evaluation benchmark)
- **Mokshi** — Backend (FastAPI, auth, DB) + Frontend (UI)

## Architecture
See [`docs/architecture.md`](docs/architecture.md)

## Tech Stack
- Backend: FastAPI, PostgreSQL, SQLAlchemy
- AI: LangChain/CrewAI, Qdrant (vector store), Groq/Gemini LLM
- Frontend: Streamlit
- CI/CD: GitHub Actions
- Deployment: Render + Neon/Supabase + Qdrant Cloud

## Setup
```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd querygenie

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # fill in your DB/Qdrant/LLM keys

# 3. Set up the database
psql <your-db-url> -f ../db/ecommerce_schema_seed.sql

# 4. Run backend
uvicorn main:app --reload

# 5. Run frontend (separate terminal)
cd ../frontend
pip install streamlit
streamlit run app.py
```

## Project Status
In progress — see `docs/` for roadmap and design docs.

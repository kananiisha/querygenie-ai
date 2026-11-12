![CI](https://github.com/kananiisha/querygenie-ai/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

<!-- After deploying on Render, add a "Live demo" link and a demo GIF under the tagline. -->

# 🔍 QueryGenie AI: Multi-Agent NL-to-SQL

Ask your business database anything in plain English. No SQL knowledge needed.

## 🎯 Problem

Non-technical teams depend on data analysts for every small data question, which slows decisions. QueryGenie AI lets anyone query a database conversationally. A multi-agent pipeline retrieves the relevant schema, writes the SQL, validates it for safety, runs it, and explains the result in plain English.

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
│   SQL Generator     │  ← Writes a SELECT query with an LLM (Groq)
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│  Validator/Safety   │  ← Blocks unsafe queries, retries with feedback
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│  Query Executor     │  ← Runs validated SQL against the database
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│     Explainer       │  ← Turns raw results into a plain-English answer
└─────────────────────┘
      │
      ▼
  Plain-English Answer + SQL + Raw Data + Confidence Score
```

| Agent | Role |
|---|---|
| Schema Retriever | Semantic search over table descriptions (sentence-transformers + Qdrant), top 4 tables |
| SQL Generator | Writes a SQLite SELECT query with `openai/gpt-oss-120b` on Groq |
| Validator | Blocks DROP/DELETE/UPDATE/ALTER and multi-statement queries; retries with feedback |
| Executor | Runs the validated SQL |
| Explainer | Converts rows into a plain-English answer |

**Also included:** in-memory result caching (100 entries) and a heuristic confidence score (schema relevance + validation retries + non-empty result). The score is a heuristic, not a calibrated probability.

## 📊 Benchmark

**Method:** 50 questions with hand-written gold SQL over the demo database (11 count, 8 filter, 1 aggregation, 10 join, 10 group-by/order-by, 5 multi-condition filter, 5 tricky: subquery/HAVING/DISTINCT). The metric is **execution accuracy**: the gold SQL and the pipeline's SQL both run on the same database and the result sets are compared (row order ignored unless the question asks for sorting; extra columns allowed; row count and every expected value must match). Run it with `python benchmark.py`.

| Run | Setup | Execution accuracy |
|---|---|---|
| Initial | Original prompt, top 2 tables retrieved, stricter scoring | 41/50 (82%) |
| After fixes | Prompt rules + top 4 tables + scoring allows extra columns | **50/50 (100%)** in the final full run; 96 to 100% across five full runs |
| Held-out | 15 new questions written after the prompt was finalized, never used to change it | 15/15 (100%). Small sample |

- **By category (final full run):** count 11/11 · filter 8/8 · aggregation 1/1 · join 10/10 · group-by 10/10 · multi-filter 5/5 · tricky 5/5
- **Latency (Groq free tier):** p50 ≈ 4.0 s, p95 ≈ 15.7 s (varies with load)
- **Safety:** 8/8 write/DDL attack prompts handled ("delete all orders", "drop table", multi-statement injection, etc.), database unchanged.

**Failures found along the way and how they were fixed**

| Failure | Count | Cause | Fix |
|---|---|---|---|
| Dropped a filter (all products returned instead of Delhi only) | 1 | Only 2 tables retrieved, so `customers` was missing from context | Retrieve top 4 tables; "never drop a filter" prompt rule |
| Returned IDs instead of names | 3 | Prompt did not force name columns on joins | "Return names, join to get them" rule |
| "How many…" returned a row list instead of a count | 2 | An old rule always added name and email for customer questions | Removed it; use `COUNT(*)` for "how many" |
| Correct values but extra columns | 3 | Scoring was too strict (the benchmark harness, not the pipeline) | Scoring now allows extra columns |
| Wrong text case (`'UPI'` vs stored `'upi'`) | 1 (found in a later run) | Model copied the case from the question | Prompt lists the exact stored value spellings |

> The prompt rules were written after seeing failures on the 50-question set, so its score is optimistic. The held-out set is a sanity check on 15 questions, not strong evidence of generalization.

## ✨ Tech Stack

| Layer | Technology |
|---|---|
| LLM | `openai/gpt-oss-120b` via Groq |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector DB | Qdrant (local embedded mode by default) |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Streamlit |
| CI/CD | GitHub Actions |

## 🚀 Setup & Run

```bash
git clone https://github.com/kananiisha/querygenie-ai.git
cd querygenie-ai
cd backend && python -m pip install -r requirements.txt && cd ..

# Create your env file, then add your GROQ_API_KEY and a random SECRET_KEY
cp backend/.env.example backend/.env        # Windows: Copy-Item backend\.env.example backend\.env

python seed_sqlite.py                        # seed the demo database (once)
python -m backend.schema_indexer.index_schema   # index the schema (once)

# Terminal 1
python -m uvicorn backend.main:app --reload
# Terminal 2
python -m streamlit run frontend/app.py
```

Open http://localhost:8501. Leave `QDRANT_URL` empty to run Qdrant locally with no server.

```bash
python -m pytest tests               # unit tests
python benchmark.py                  # full benchmark: 50 questions + 8 safety tests
python benchmark.py --heldout        # 15 held-out questions
python benchmark.py --ids=1,2        # rerun specific questions
```

The benchmark uses many Groq tokens (the free tier has a daily limit). Stop the backend before running it, because local Qdrant storage allows only one process at a time.

## 📁 Project Structure

```
querygenie-ai/
├── .github/workflows/      # CI
├── backend/
│   ├── agents/             # sql_generator, validator, executor, explainer, pipeline
│   ├── schema_indexer/     # schema_metadata, index_schema, retrieve_schema
│   ├── main.py  database.py  auth.py  file_ingestion.py
│   └── .env.example
├── frontend/app.py
├── tests/
├── benchmark.py            # execution-accuracy benchmark, held-out set, safety suite
├── benchmark_results.json
├── benchmark_results_heldout.json
├── seed_sqlite.py  seed_neon.py
└── render.yaml             # Render deployment config
```

## 🔒 Security

- **SELECT-only validation:** `backend/agents/validator.py` blocks DROP, DELETE, UPDATE, ALTER and multi-statement queries before execution. Checked by the safety suite in `benchmark.py`.
- **JWT authentication** (`backend/auth.py`): login issues signed tokens. By default, requests without a token run as a shared demo user so the public demo works without sign-up. Set `ALLOW_ANONYMOUS=false` to require a token. In production, the app refuses to start without a real `SECRET_KEY`.
<!-- VERIFY each line below in the code before keeping it. Delete any you cannot point to a file for:
- Read-only database connection (which file/setting enforces it?)
- Audit log of every query (which file writes it?)
- Prompt-injection protection (what exactly does it do?)
-->

## ⚠️ Limitations

- The demo database is small (10 customers, 12 products, 15 orders), so scores do not reflect real-world schemas.
- Gold SQL was written by the project author, and the prompt was tuned on the main 50-question set. The held-out set has only 15 questions.
- LLM output is not fully deterministic, so scores vary slightly between runs. Groq free-tier limits apply.
- Multi-table joins were the hardest category in the initial run. SELECT queries only; no write operations by design.

## 🛣️ Next Steps

- Deploy a live demo and add a short demo GIF.
- Evaluate on a public NL-to-SQL set (a Spider subset) for an external number.
- Move retry counting into the validator instead of patching the generator in `pipeline.py`.

## 📄 License

MIT. See [LICENSE](LICENSE).
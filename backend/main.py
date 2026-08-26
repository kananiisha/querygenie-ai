"""
FastAPI application — main entry point.
"""
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy.datasets import clear_cache
from sqlalchemy.orm import Session

from backend.database import get_db, init_db, QueryLog
from backend.auth import hash_password, verify_password, create_access_token

app = FastAPI(title="QueryGenie AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    try:
        from backend.schema_indexer.index_schema import build_schema_index
        build_schema_index()
        print("Schema indexed successfully on startup.")
    except Exception as e:
        print(f"Schema indexing failed on startup: {e}")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    from backend.database import User
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(email=req.email, hashed_password=hash_password(req.password))
    db.add(user)
    db.commit()
    return {"message": "Registered successfully."}


@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    from backend.database import User
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


# ─── File Upload ───────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        import os as _os
        allowed = [".csv", ".xlsx", ".xls"]
        ext = _os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(status_code=400, detail="File type not supported. Use CSV or Excel.")

        file_bytes = await file.read()
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > 500:
            raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.0f}MB). Max 500MB.")

        from backend.file_ingestion import ingest_file, index_uploaded_schema
        metadata = ingest_file(file_bytes, file.filename)
        index_uploaded_schema(metadata)

        from backend.agents.pipeline import clear_cache
        clear_cache()

        return {
            "status": "success",
            "table_name": metadata["table_name"],
            "filename": metadata["original_filename"],
            "rows": metadata["row_count"],
            "columns": metadata["columns"],
            "size_mb": metadata["size_mb"],
            "message": f"Successfully processed {metadata['row_count']:,} rows.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tables")
def list_tables():
    from backend.file_ingestion import list_uploaded_tables
    return {"tables": list_uploaded_tables()}


# ─── Query ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    table_hint: str | None = None


@app.post("/query")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    try:
        from backend.agents.pipeline import run_pipeline
        output = run_pipeline(req.question, table_hint=req.table_hint)

        log = QueryLog(
            question=req.question,
            generated_sql=output["sql"],
            status="success"
        )
        db.add(log)
        db.commit()

        return {
            "question": output["question"],
            "sql": output["sql"],
            "results": output["results"],
            "answer": output["answer"],
            "status": "success",
        }

    except Exception as e:
        log = QueryLog(question=req.question, generated_sql=None, status="failed")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query/history")
def query_history(db: Session = Depends(get_db)):
    logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(20).all()
    return [
        {
            "id": l.id,
            "question": l.question,
            "sql": l.generated_sql,
            "status": l.status,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]
@app.post("/recommendations")
def get_recommendations(req: QueryRequest):
    """
    Generates smart question recommendations based on
    the active dataset's schema and sample data.
    """
    try:
        import os
        from groq import Groq
        from backend.schema_indexer.retrieve_schema import get_relevant_tables

        # Get schema context
        schema_context = get_relevant_tables(
            "show me everything about this dataset",
            top_k=3
        )

        if req.table_hint:
            schema_context = [s for s in schema_context
                            if s["table"] == req.table_hint][:1] or schema_context[:1]

        schema_text = "\n".join([
            f"Table: {s['table']}, Columns: {', '.join(s['columns'][:15])}"
            for s in schema_context
        ])

        client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a data analyst. Generate exactly 6 useful business questions a non-technical user could ask about this dataset. Return ONLY a JSON array of 6 strings, nothing else. Example: [\"How many rows?\", \"What is the total sales?\"]"
                },
                {
                    "role": "user",
                    "content": f"Dataset schema:\n{schema_text}\n\nGenerate 6 smart questions:"
                }
            ],
            temperature=0.7,
            max_tokens=300,
        )

        import json
        raw = response.choices[0].message.content.strip()
        # Clean markdown if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        questions = json.loads(raw)
        return {"recommendations": questions[:6]}

    except Exception as e:
        # Fallback to generic questions if LLM fails
        return {"recommendations": [
            "How many rows are in this dataset?",
            "What are the unique values in the first column?",
            "Show me the top 5 records",
            "What is the total count by category?",
            "Show me records from the last month",
            "What is the average value?",
        ]}
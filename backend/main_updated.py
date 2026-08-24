"""
Complete updated main.py — includes the /upload endpoint
Replace your entire backend/main.py with this file
"""

import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
        print(f"Schema indexing on startup: {e}")


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
    """
    Accepts CSV or Excel files, creates a SQLite table,
    and indexes schema into Qdrant for querying.
    """
    try:
        allowed = [".csv", ".xlsx", ".xls"]
        import os as _os
        ext = _os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not supported. Use CSV or Excel."
            )

        file_bytes = await file.read()
        if len(file_bytes) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

        from backend.file_ingestion import ingest_file, index_uploaded_schema
        metadata = ingest_file(file_bytes, file.filename)
        index_uploaded_schema(metadata)

        return {
            "status": "success",
            "table_name": metadata["table_name"],
            "filename": metadata["original_filename"],
            "rows": metadata["row_count"],
            "columns": metadata["columns"],
            "message": "File uploaded successfully. You can now ask questions about your data.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

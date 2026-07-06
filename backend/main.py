"""
FastAPI application — main entry point.
"""

from fastapi import FastAPI, Depends, HTTPException
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


@app.get("/health")
def health_check():
    return {"status": "ok"}


# ─── Auth ────────────────────────────────────────────────────────────────────

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


# ─── Query ───────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    Main endpoint — runs the full agent pipeline and returns
    question, SQL, raw results, and plain-English answer.
    """
    try:
        from backend.agents.pipeline import run_pipeline
        output = run_pipeline(req.question)

        # Log to DB
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

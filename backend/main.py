from fastapi import FastAPI

app = FastAPI(title="QueryGenie AI")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# /query, /schema, /auth endpoints will be added here as the project grows

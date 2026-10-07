from fastapi import FastAPI

app = FastAPI(title="SecureMCP")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

from fastapi import FastAPI

from app.api.routes_agent import router as agent_router

app = FastAPI(title="SecureMCP")
app.include_router(agent_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

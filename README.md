# SecureMCP

Security gateway between an LLM agent and its tools: ALLOW / FLAG / BLOCK before a tool runs.
Research question: do lightweight black-box gateways survive unseen attack families, adaptive
attacks, and honest-but-promotional descriptions, and does tool-set structure change that?

## Setup (Windows, PowerShell)

Requires Python 3.11 (NOT 3.14), Node 22, Docker Desktop, Git.

```powershell
# 1. Python env (from repo root)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --port 8000     # http://127.0.0.1:8000/health

# 2. Node API (new terminal)
cd api-node
npm install
npm test
npm run dev                                   # http://127.0.0.1:3001/health

# 3. MongoDB (new terminal, Docker running)
docker compose up -d mongo
```

Later (Phase 4+), light ML on the laptop, CPU-only torch first:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[ml]"
```

Heavy work (dataset generation, S1 fine-tuning, the 7-8B LLM) runs on Colab, never the laptop.

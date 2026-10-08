# SecureMCP

[![CI](https://github.com/RajyalakshmiKillamsetty2023/securemcp/actions/workflows/ci.yml/badge.svg)](https://github.com/RajyalakshmiKillamsetty2023/securemcp/actions/workflows/ci.yml)

A security gateway between an LLM agent and its tools. Before a tool runs, the gateway scores the
agent's choice and returns **ALLOW**, **FLAG** or **BLOCK**.

## Research question

Do lightweight, black-box gateways survive **unseen attack families**, **adaptive (rewritten)
attacks** and **honest-but-promotional tool descriptions**, and does tool-set similarity or
ordering change the result?

Layered gateways and embedding detectors already exist (MCP-Guard, CASCADE, MindGuard, MSB).
The contribution of this project is the evaluation study, not the gateway itself.

## How it works

The gateway combines three signals with a learned fusion model and calibrated thresholds.

| Signal | Question it answers | Method |
|---|---|---|
| S1 Description risk | Is the description normal, promotional or malicious? | TF-IDF + LogReg baseline, fine-tuned embedding classifier |
| S2 Query-tool relevance | Does the chosen tool fit the request? | Bi-encoder cosine similarity |
| S3 Selection consistency | Does the choice change with neutral descriptions? | Black-box re-selection |

## Architecture

```
React dashboard  →  Node API (thin layer)  →  FastAPI (agent, gateway, ML, experiments)  →  MongoDB
```

Heavy work (dataset generation, S1 fine-tuning, the 7-8B agent LLM, large experiments) runs on a
free Colab T4. The laptop runs the dashboard, APIs, gateway scoring and small models only.
All tools are fake, sandboxed functions that return canned data.

## Status

| Phase | Scope | State |
|---|---|---|
| 0 | Foundation: repo, CI, environment, Colab setup | In progress |
| 1 | Python agent core | Planned |
| 2 | End-to-end vertical slice | Planned |
| 3 | Dataset | Planned |
| 4 | Detector and baselines | Planned |
| 5 | Gateway | Planned |
| 6 | Dashboard and core experiments | Planned |
| 7 | Factor study, adaptive attacker, trade-off | Planned |
| 8 | Hardening and replay mode | Planned |
| 9 | Report and demo | Planned |

## Quick start (Windows, PowerShell)

Requirements: Python 3.11 (not 3.14), Node 22, Docker Desktop, Git.

```powershell
# Backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --port 8000     # http://127.0.0.1:8000/health

# Node API (new terminal)
cd api-node
npm install
npm test
npm run dev                                   # http://127.0.0.1:3001/health

# MongoDB (new terminal, Docker running)
docker compose up -d mongo                    # host port 27018
```

Colab: open `notebooks/00_colab_setup.ipynb` and choose **Runtime → Run all**.

## Repository layout

```
backend/      FastAPI app, gateway, ML code, data build scripts, experiments
api-node/     Express layer (validation, rate limiting, event stream)
dashboard/    React dashboard (added in Phase 2)
notebooks/    Colab notebooks for GPU work
docs/         Threat model, experiment plan, literature table, dataset and model cards
```

## Data

MCPTox (external test set), MSB, and BFCL (normal tools and queries). Licences are checked
before any dataset is downloaded. Raw data is not committed.

## Changelog

### Phase 0 (in progress)
- Repository skeleton, CI (ruff, pytest, Node tests), MongoDB via Docker Compose
- Minimal FastAPI and Express apps with health endpoints and tests
- Colab setup notebook
- Threat model, experiment plan and literature table drafted

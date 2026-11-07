# SecureMCP

[![CI](https://github.com/RajyalakshmiKillamsetty2023/securemcp/actions/workflows/ci.yml/badge.svg)](https://github.com/RajyalakshmiKillamsetty2023/securemcp/actions/workflows/ci.yml)

A security gateway for LLM agents. Before the tool an agent has chosen is executed, SecureMCP scores
the choice and returns **ALLOW**, **FLAG** or **BLOCK**.

Tool descriptions in MCP-style systems are written by third parties, so a crafted description can steer
an agent toward the wrong tool. SecureMCP checks for this at selection time and treats the model as a
black box. The repository also contains an evaluation study of how well such lightweight gateways hold
up against unseen attack families, adaptive attacks and honest promotional descriptions.

## How it works

Each decision combines three signals with a learned fusion model and calibrated thresholds.

| Signal | Question | Method |
|---|---|---|
| S1 Description risk | Is the description normal, promotional or malicious? | TF-IDF + logistic regression baseline; fine-tuned embedding classifier |
| S2 Query-tool relevance | Does the chosen tool fit the request? | Bi-encoder cosine similarity |
| S3 Selection consistency | Does the choice change when descriptions are neutralised? | Black-box re-selection |

```
React dashboard -> Node API -> FastAPI (agent, gateway, ML, experiments) -> MongoDB
```

All tools are fake, sandboxed functions that return canned data. Training and large experiments run on
a free Colab GPU; everything else runs on a laptop.

## Getting started

**Requirements:** Python 3.11, Node 22, Docker, Git.

```powershell
# Backend (Windows PowerShell)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

On macOS or Linux: `python3.11 -m venv .venv && source .venv/bin/activate`.

```bash
# Node API (separate terminal)
cd api-node && npm install && npm run dev

# MongoDB (host port 27018)
docker compose up -d mongo
```

## Usage

Open the interactive API docs at <http://127.0.0.1:8000/docs>, or send a request:

```
POST /agent/run
{"query": "What is 15 * 4?"}
```

Abridged response:

```json
{
  "call": {"tool": "calculator", "arguments": {"expression": "15 * 4"}},
  "executed": true,
  "result": {"ok": true, "output": {"expression": "15 * 4", "result": 60}},
  "gateway": null
}
```

`gateway` stays empty until the gateway is implemented.

## Configuration

Settings are read from environment variables or a `.env` file (see `.env.example`).

| Variable | Default | Purpose |
|---|---|---|
| `LLM_MODE` | `mock` | `mock` (offline, development only), `ollama`, `openai_compat`, or `replay` (cache only) |
| `LLM_MODEL` | `qwen2.5:7b-instruct` | Model name for `ollama` / `openai_compat` |
| `LLM_CACHE_PATH` | `llm_cache.jsonl` | Response cache; point it at Google Drive on Colab |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server |
| `MONGO_URI` | `mongodb://127.0.0.1:27018` | MongoDB connection |

`mock` is a keyword matcher, not a language model. Do not use it for experiments.

## Testing

```bash
cd backend && ruff check . && pytest -q
cd api-node && npm test
```

## Data

The study uses [BFCL](https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard)
(Apache-2.0), [MSB](https://huggingface.co/datasets/DongsenZhang/MSB) (MIT) and
[MCPTox](https://github.com/zhiqiangwang4/MCPTox-Benchmark) (no licence file; research use with
citation), plus a dataset built for this project. Raw data is not committed.

```bash
cd backend && pip install -e ".[ml]" && python data/download_raw.py
```

Sources, licences and handling rules: [`docs/dataset_card.md`](docs/dataset_card.md),
[`docs/decisions.md`](docs/decisions.md).

## Project structure

```
backend/      FastAPI service: agent, gateway, ML, data build scripts, experiments, tests
api-node/     Express layer: validation, rate limiting, live event stream
dashboard/    React dashboard
notebooks/    Colab notebooks for GPU work
docs/         Threat model, experiment plan, literature table, dataset and model cards
```

## Documentation

- [Threat model](docs/threat_model.md)
- [Experiment plan](docs/experiment_plan.md)
- [Literature table](docs/literature_table.md)
- [Decisions log](docs/decisions.md)

## Roadmap

- [x] Agent core and sandboxed fake tools
- [ ] Storage, Node API and live dashboard
- [ ] Dataset (normal, promotional and malicious descriptions)
- [ ] Detector and baselines
- [ ] Gateway and policy
- [ ] Experiments and final report

See [CHANGELOG.md](CHANGELOG.md) for what has changed so far.

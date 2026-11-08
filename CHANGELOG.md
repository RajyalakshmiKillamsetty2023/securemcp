# Changelog

All notable changes to this project are recorded here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Run storage: every agent call is saved to MongoDB (in-memory option for tests), with `GET /logs` and
  `GET /logs/{id}`.
- Structured JSON logging with a request ID that follows a call from the Node API through Python into
  the stored record.
- Node API: validated `POST /api/agent/run`, `GET /api/logs`, `GET /api/logs/{id}`, and a server-sent
  events stream at `GET /api/events`, with timeouts, safe retries and rate limiting.
- React dashboard with a live table of agent calls and a query form.
- Architecture document.
- Colab notebook section that runs the agent against a real model through Ollama and checks that a
  second pass is served from the cache.
- Agent core: typed schemas, settings, tool registry (tool count and ordering), versioned selection
  prompt, tolerant output parser, validating executor.
- `POST /agent/run` endpoint and a smoke script.
- LLM layer: abstract client, JSONL response cache, Ollama and OpenAI-compatible clients,
  cache-only replay mode, and an offline mock for development.
- Ten fake sandboxed tools, with a test that bans file, network and process access.
- Dataset download script with a hash manifest (MCPTox, BFCL, MSB).
- Dataset card draft and decisions log (implicit-poisoning scope, LLM setup, dataset licences).

### Changed
- `POST /agent/run` responses now include `created_at` and `logged`.
- Default model tag is `qwen2.5:7b` (the tag listed in the Qwen documentation).
- Node tests run with `node --test`, which works across Node 22 releases.
- Threat model: success now covers implicit hijacks; S1 scores every offered description.
- Node API uses zod 4 (resolves a reported memory-exhaustion advisory).

## [0.1.0] - Foundation

### Added
- Repository skeleton, CI (ruff, pytest, Node tests), MongoDB via Docker Compose.
- Minimal FastAPI and Express apps with health endpoints and tests.
- Colab setup notebook (GPU check, Drive persistence, repo clone, embedding model, smoke test).
- Threat model, experiment plan and literature table.

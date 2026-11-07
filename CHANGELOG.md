# Changelog

All notable changes to this project are recorded here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Agent core: typed schemas, settings, tool registry (tool count and ordering), versioned selection
  prompt, tolerant output parser, validating executor.
- `POST /agent/run` endpoint and a smoke script.
- LLM layer: abstract client, JSONL response cache, Ollama and OpenAI-compatible clients,
  cache-only replay mode, and an offline mock for development.
- Ten fake sandboxed tools, with a test that bans file, network and process access.
- Dataset download script with a hash manifest (MCPTox, BFCL, MSB).
- Dataset card draft and decisions log (implicit-poisoning scope, LLM setup, dataset licences).

### Changed
- Threat model: success now covers implicit hijacks; S1 scores every offered description.

## [0.1.0] - Foundation

### Added
- Repository skeleton, CI (ruff, pytest, Node tests), MongoDB via Docker Compose.
- Minimal FastAPI and Express apps with health endpoints and tests.
- Colab setup notebook (GPU check, Drive persistence, repo clone, embedding model, smoke test).
- Threat model, experiment plan and literature table.

# Architecture

## Overview

```
React dashboard  ->  Node API  ->  FastAPI  ->  LLM client  ->  Ollama (Colab) / mock (laptop)
     ^                 |             |
     |  server-sent    |             +-> fake tools (sandboxed)
     +---- events -----+             +-> MongoDB (runs)
```

The gateway (S1, S2, S3, fusion, policy) will sit inside FastAPI between "model chooses a tool" and
"tool runs". It is not implemented yet.

## Components

| Component | Responsibility |
|---|---|
| Dashboard (`dashboard/`) | Query form, live table of calls. Talks only to the Node API |
| Node API (`api-node/`) | Input validation, rate limiting, request IDs, timeouts and retries, live event stream. Holds no state and does not touch the database |
| FastAPI (`backend/app/`) | Agent, tools, LLM clients and cache, run storage, logs endpoints |
| MongoDB | One document per run in the `runs` collection |
| Ollama | Serves the 7-8B model. Runs on Colab, not on the laptop |

## Request flow

1. The dashboard posts a query to `POST /api/agent/run`.
2. Node validates it, creates a request ID and calls `POST /agent/run` on FastAPI with an
   `X-Request-ID` header.
3. FastAPI builds the tool list, asks the LLM to choose, parses the reply, runs the fake tool and
   saves the run with the same request ID.
4. Node publishes the finished run to the event stream and returns it to the caller.
5. Every open dashboard receives a `run` event and adds the row.

## Stored run

| Field | Meaning |
|---|---|
| `request_id`, `created_at` | Identity and UTC time |
| `query`, `request` | The user's query and the options sent (`n_tools`, `order`, `seed`) |
| `model`, `prompt_version` | What produced the choice |
| `tools_offered` | Tool names in the order the model saw them |
| `call` | Chosen tool, arguments, raw model output, parse error if any |
| `executed`, `result` | Whether a tool ran and what it returned |
| `gateway` | Empty until Phase 5; will hold the decision and the three signal scores |
| `latency_ms` | Time spent in the agent |

## Logging

Both services write JSON log lines. The request ID created in Node appears in the Node log, the Python
log and the stored run, so one call can be followed end to end.

## Failure behaviour

| Situation | Result |
|---|---|
| Invalid request body | Node answers 400 and never calls Python |
| `n_tools` larger than the catalog | 422 from Python, passed through |
| LLM unreachable or cache miss in replay mode | 502 |
| Python service down | Node answers 502 |
| Python service too slow | Node answers 504 |
| MongoDB down while running a query | The call succeeds with `logged: false` |
| MongoDB down while reading logs | 503 |

## Where things run

The laptop runs the dashboard, Node, FastAPI, MongoDB and the offline mock. Model serving, training and
large experiments run on Colab and write results to Google Drive.

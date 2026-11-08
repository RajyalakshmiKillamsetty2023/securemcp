# Decisions log

Dated, one entry per decision. Changes to frozen items go in `experiment_plan.md` under Amendments.

## 2026-10-08

### D1. Implicit poisoning is in scope for hijacking, out of scope for argument tampering
MCP-ITP and many MCPTox cases use a poisoned description on a tool that is never called, which makes
the agent call a different legitimate tool or alter a parameter.
- **In scope:** the agent's chosen tool is wrong for the query because of poisoned descriptions in the
  offered set (choice hijack, including implicit).
- **Out of scope:** parameter tampering after the correct tool is chosen (already excluded in the threat model).
- **Design consequence:** S1 scores every offered description and takes the maximum risk. S2 and S3
  score the chosen tool against the query.
- **MCPTox use:** S1 is evaluated on all MCPTox poisoned descriptions. The full gateway (S1+S2+S3) is
  evaluated only on the hijack-type cases.

### D2. LLM setup
- Agent LLM: one 7-8B instruct model served by Ollama on Colab. Every response is cached by
  hash(model + prompt) on Drive.
- A hosted API stays an optional fallback behind `openai_compat_client` and is not required.
- Laptop default is `LLM_MODE=replay`, so the demo never needs a live model.

### D3. Dataset licences and handling
| Dataset | Source | Licence | Handling |
|---|---|---|---|
| BFCL | Hugging Face `gorilla-llm/Berkeley-Function-Calling-Leaderboard` | Apache-2.0 | Download the JSON files directly; its README says not to use `load_dataset` |
| MSB | Hugging Face `DongsenZhang/MSB` | MIT | Use data files only. Do not download or run `data/tools/` (server launch configs; at least one contains what looks like a hard-coded credential) |
| MCPTox | github.com/zhiqiangwang4/MCPTox-Benchmark | No licence file (checked: LICENSE returns 404, README contains only a title) | Research use with citation. Do not redistribute or commit the raw files (gitignored). Email the authors before publishing any derived data |

### D4. Attack-paper figures
FHA figures in the literature table follow the paper found at arXiv 2604.20994 (70% to 98% function-name
ASR over 200 BFCL payloads, 5 models). The earlier "62.5% to 81.9% across 4 models" could not be
matched to any source and is not used.

### D5. Thresholds frozen
Target FPR 5% (second point 1%); unseen-family survival within 10 points; adaptive survival above 50% of
round-0 detection; promotional-safe at no more than 2x normal FPR.

### D6. Attack code availability (checked 2026-10-08)
| Paper | Public code? | Consequence |
|---|---|---|
| ToolHijacker | No. Repo exists but states the code is not public; available on request for academic use | Not needed. Optional: email the authors |
| FHA | None found. It adapts a white-box gradient attack (GCG), outside our threat model | Not needed |
| MCP-ITP | No official code found | Rebuild the loop ourselves; the paper describes it (attacker LLM, detector LLM, effectiveness LLM, iterate with feedback) |

Decision: the adaptive attacker in E6 is our own black-box rewriting loop (3 rounds, detector feedback),
as the plan already allowed. Third-party demo repos found (Invariant Labs PoC, others) are not used.

## 2026-11-08

### D6. Saving a run is best-effort
If MongoDB is unreachable, the agent call still returns normally with `logged: false`, and the error is
logged. A storage outage must not stop the agent.

### D7. Retry rules in the Node layer
GET requests retry on connection errors and on 502, 503 and 504. `POST /agent/run` is retried only when
no connection was made, never after a response, so a run cannot execute or be stored twice.

### D8. Model tag
The Ollama tag is `qwen2.5:7b`, as listed in the Qwen documentation, which also states that untagged
Qwen2.5 variants are instruct models. It replaces `qwen2.5:7b-instruct`, which was never checked.


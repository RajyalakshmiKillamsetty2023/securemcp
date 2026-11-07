# Dataset card (draft, completed in Phase 3)

## External sources
| Source | Licence | What we use | Notes |
|---|---|---|---|
| MCPTox | none visible (research use, cite, do not redistribute) | `pure_tool.json`: 485 poisoned tool entries across 45 servers, each with query, poisoned description, risk category and template; `response_all.json`: 1,348 cases, plus per-server clean prompts and queries | No separate benign class: benign descriptions sit inside each server's clean system prompt and must be extracted |
| BFCL | Apache-2.0 | Normal tools and queries (simple, multiple, live) | Do not load with `datasets.load_dataset` |
| MSB | MIT | Attack and task data files only | `data/tools/` is not used |

## Own data (built in Phase 3)
About 800 descriptions: ~250 normal, ~250 promotional, ~300 malicious (6 families x ~50).
Sizes, class balance and known limits are added when `validate_dataset.py` passes.

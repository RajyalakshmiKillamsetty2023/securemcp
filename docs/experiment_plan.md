# Experiment plan

Written before any experiment is run. Hypotheses, metrics and decision rules below must not be
changed after results are seen. Any change goes in a dated "Amendments" section at the end.

## Global protocol
- **Splits:** grouped by source tool and attack family. Splits are frozen at the end of Phase 3.
  Test sets are never used for tuning, threshold selection or model choice.
- **Seeds:** 3 to 5 per experiment. Report mean and 95% bootstrap CI.
- **Threshold policy:** thresholds chosen on benign validation data for a target FPR (default 5%,
  fixed here before running; a second operating point at 1%).
- **Reproducibility:** every run is defined by a YAML config under `backend/experiments/configs/`
  and saved under a run ID. LLM calls are cached by hash(model + prompt).
- **Metrics:** precision, recall, F1, ROC-AUC, FPR (reported separately for normal and promotional),
  attack success rate (ASR), benign task success.

## Experiments

| ID | Question | Setup | Metrics | Hypothesis |
|---|---|---|---|---|
| E1 | How accurately does the agent select tools with no attack? | BFCL queries, varying N | Selection accuracy | Accuracy falls as N grows (baseline for E5) |
| E2 | Does the detector generalize? | Train on 5 families, test on the held-out one (leave-one-family-out); also in-distribution and MCPTox | Recall at fixed FPR, F1, AUC | Recall drops on unseen families and on MCPTox relative to in-distribution |
| E3 | Which signals matter? | S1, S2, S3 alone, pairs, fusion; vs keyword filter, LLM judge, MCP-Guard-style baseline | Recall at fixed FPR, AUC | Fusion beats any single signal; S1 is strongest in-distribution, S2/S3 help on unseen families |
| E4 | Are honest promotional descriptions wrongly blocked? | Promotional class only | FPR on promotional vs on normal | Promotional FPR exceeds normal FPR for every detector; the gap is largest for the keyword filter |
| E5 | Do tool count, similarity and order change the defense? | N in 4..64, similarity levels, order permutations; gateway off vs on | ASR, benign success, recall at fixed FPR | ASR rises with N and similarity; position effects exist; the gateway reduces but does not remove them |
| E6 | Does the gateway survive adaptive attacks? | 3 rewriting rounds against detector feedback (A1); then retrain and re-evaluate | Detection rate per round, before and after retraining | Detection decays across rounds; retraining recovers only part of it |
| E7 | What does security cost in utility? | Threshold sweep | ASR vs benign task success curve; MSB's NRP as defined in its paper | A usable operating point exists but with measurable utility loss |
| E8 | What is the latency cost? | Per-stage timing on laptop | p50 and p95 for S1, S2, S3, fusion | S3 dominates latency because it re-runs selection |

## Decision rules (what counts as an answer)
- **Survives unseen families:** recall on the held-out family is within 10 points of in-distribution
  recall at the same FPR. Otherwise it does not survive.
- **Survives adaptive attack:** detection after round 3 stays above 50% of round-0 detection.
- **Promotional-safe:** promotional FPR is no more than 2x the normal FPR.
- Negative results are reported as findings, not hidden.

## Threats to validity
- LLM-generated attacks may share stylistic artifacts that detectors learn (checked by
  `validate_dataset.py` for templates and near-duplicates).
- One agent model; small dataset (~800 descriptions); wide CIs are expected and will be reported.
- Promotional descriptions are LLM-written; a hand-checked sample guards label quality.

## Amendments
_None yet._

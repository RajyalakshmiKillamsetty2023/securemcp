# Literature table

Compiled 2026-10-08 from abstracts and search summaries. The "does not cover" column is my reading
of what each paper reports; confirm against the full text before the final report cites it.

## Core papers

| Paper | Role | Data | Headline result | Does not cover (relative to this project) | Link |
|---|---|---|---|---|---|
| **MCPTox** (Wang et al., AAAI) | Benchmark of tool-poisoning attacks | 45 live MCP servers, 353 tools, 10 risk categories, three attack templates; 1,348 cases in the AAAI version (1,312 in arXiv v1) | 20 agents tested; highest ASR 72.8%; more capable models were often more vulnerable | Measures agent vulnerability, not detector or gateway generalization; no honest-promotional class | arXiv 2508.14925 |
| **MSB** (Zhang et al., ICLR 2026) | Benchmark of MCP attacks across planning, invocation, response | 12 attack types, 2,000 attack instances, 405 tools, 10 domains, real tool execution | 9 agents tested; defines Net Resilient Performance, NRP = PUA x (1 - ASR) | Evaluates agents, not description detectors; no unseen-family or adaptive-rewrite protocol for a gateway | arXiv 2510.15994; code github.com/dongsenzhang/MSB |
| **ToolHijacker** (Shi et al., NDSS) | Attack: optimized malicious tool document for retrieval-then-selection pipelines | No-box setting, shadow LLM, two-phase optimization | Beats manual and automated injection baselines; tested defenses (StruQ, SecAlign, known-answer detection, DataSentinel, perplexity, windowed perplexity) were insufficient | No learned description classifier or relevance/consistency gateway tested; no promotional-text false alarms | arXiv 2504.19793 |
| **FHA** (function hijacking, 2026) | Attack: gradient-trained adversarial text in function descriptions, including universal functions | BFCL, 5 models | 70% to 100% ASR over BFCL | Gradient (white-box-style) optimization is outside our threat model; no gateway evaluation | arXiv 2604.20994 |
| **MCP-ITP** (Li et al., 2026) | Attack: automated implicit tool poisoning; attacker LLM refines descriptions using feedback from a detector LLM and an effectiveness LLM | MCPTox, 12 agents | Up to 84.2% ASR while detection rate falls as low as 0.3% | Detector in the loop is an LLM judge, not an embedding or relevance gateway; poisoned tool is never invoked, so it targets a different success condition (see note 1) | arXiv 2601.07395 |
| **MCP-Guard** (Xing et al.) | Defense: three stages (static scan, fine-tuned E5 detector, LLM arbitration) | MCP-AttackBench, 70,448 GPT-4-augmented samples | E5 stage reports 96.01% accuracy (v4); full pipeline about 89% accuracy and F1 (v1) | No leave-one-family-out test, no adaptive attacker, no promotional benign class reported | arXiv 2508.10991 |
| **MindGuard** (Wang et al.) | Defense: decision-level, attention-based Decision Dependence Graph; detects and attributes poisoned calls | Multiple MCP servers and agent LLMs | Reported as outperforming adapted baselines | Needs the agent LLM's attention weights, so it is not black-box; our gateway assumes text and choice only | arXiv 2508.20412 |
| **CASCADE** | Defense and corpus audit: regex, phrase weighting, entropy; BGE embedding with a local LLM fallback; output filter | Audited corpus of MCP attacks | Strong on exfiltration and prompt injection; weaker recall on tool poisoning (59.9%) and semantic attacks (52.5%) | Not designed around held-out attack families or adaptive rewriting; promotional false alarms not the focus | arXiv 2604.17125 |

## Closely related papers found during this search

| Paper | Why it matters here | Link |
|---|---|---|
| **AMA, Attractive Metadata Attack** (NeurIPS 2025) | Black-box iterative rewriting of names and descriptions; 81% to 95% ASR; reported to survive prompt-level defenses and auditor-based detection. Supports the A1 attacker design | arXiv 2508.02110 |
| **ToolTweak** | Gradient-free iterative rewriting; selection rate rises from about 20% to as high as 81%; proposes a paraphrase defense where the LLM restates descriptions objectively. Very close to S3 | arXiv 2510.02554 |
| **MCP-TDP benchmark ("When the Manual Lies")** | ASR above 82% for most models; reports that simple perimeter guardrails can be bypassed or backfire | arXiv 2605.24069 |

## Notes that affect the plan

1. **Success condition.** MCP-ITP's implicit poisoning makes the agent call a different, legitimate
   tool while the poisoned tool is never invoked. `threat_model.md` defines success as selecting the
   malicious tool. Either list implicit poisoning as out of scope or amend the definition. Related
   design question: should S1 score only the chosen tool's description, or every offered description?
2. **FHA numbers.** The earlier project summary quotes 62.5% to 81.9% ASR across 4 models. The paper
   found here reports 70% to 100% across 5 models. Confirm which version or paper the earlier
   figures came from before citing either.
3. **S3 novelty.** ToolTweak's paraphrase defense and counterfactual re-execution work overlap with
   S3. Keep S3 labelled as a baseline.
4. **Gateway novelty.** Layered gateways with embedding detectors exist (MCP-Guard, CASCADE). The
   contribution stays the evaluation: held-out families, adaptive attacks, promotional false alarms,
   tool-set structure.
5. **E7 metric.** NRP = PUA x (1 - ASR), taken from MSB. Check how MSB defines PUA before coding it.
6. **Still unconfirmed:** whether code for FHA, ToolHijacker or MCP-ITP is public, and the MCPTox
   and MSB licences.

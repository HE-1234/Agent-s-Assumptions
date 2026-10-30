# Evidence register for the dataset selection review

Search date: October 25, 2026. Companion to [the review](</Users/erichuang/Documents/research/projects/Agent's Assumptions/dataset_selection_review_2026-10-25.md>). The existing Stage 1 data and results were excluded from the evidence base.

The register contains **35 named source families or studies**. It is a curated set, not a deduplicated count of every search result. Related versions are grouped where noted. Secondary pages were used only to locate primary sources. No benchmark was executed.

Verification levels: **P** = primary paper/project publication; **R** = official repository/documentation/dataset card; **S** = selected task/schema/evaluator inspected. S does not mean that every task or a complete environment was audited. **X** would indicate execution; no entry reached X.

## Source register

| # | Source | Verification and limit | Decision for this study |
|---|---|---|---|
| 1 | [Terminal-Bench](https://arxiv.org/abs/2601.11868) | P/R/S; selected instructions, environments and tests | Core, after per-gap validation |
| 2 | [BigCodeBench](https://github.com/bigcode-project/bigcodebench) | R/S; some long task fields truncated in viewer | Small capability-control subset |
| 3 | [DS-1000](https://ds1000-code-gen.github.io/) | P/R/S; selected records and evaluation format | Analysis reserve |
| 4 | [InfiAgent-DABench / DAEval](https://arxiv.org/abs/2401.05507) | P/R/S; question records and grading documentation | Reserve; repair contradictions and clarify data license |
| 5 | [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) | P/R; derivative task rows and primary audit also checked | External repository-work comparison |
| 6 | [BIRD-Interact](https://arxiv.org/abs/2510.05318) | P/R/S; public rows; gold SQL/test access not obtained | Interactive SQL comparator |
| 7 | [Agent-Diff](https://arxiv.org/abs/2602.11224) | P/R/S; tasks, declarative assertions and API schema | Core workspace source |
| 8 | [AppWorld](https://aclanthology.org/2024.acl-long.850/) | P/R/S for generator architecture; protected task bundles not inspected | Rich-workflow confirmation after task audit |
| 9 | [ToolSandbox](https://arxiv.org/abs/2408.04682) | P/R/S; scenarios, knowledge separation, milestones | Diagnostic infrastructure and selected tasks |
| 10 | [WorkArena / WorkArena++](https://github.com/ServiceNow/WorkArena) | P/R/S; product configurations and validator | Finite-option browser replication |
| 11 | [AgentDojo](https://github.com/ethz-spylab/agentdojo) | R/S; benign task definitions and state utility | Compact independent action subset |
| 12 | [τ-bench / τ²-bench](https://arxiv.org/abs/2506.07982) | P/R/S; retail tasks, policy and evaluator documentation | Separate policy stratum |
| 13 | [Gaia2 / ARE](https://arxiv.org/abs/2602.11964) | P/R; dataset schema, no complete scenario audit | Later dynamic-world generalization |
| 14 | [WebArena / WebArena-Verified](https://arxiv.org/abs/2307.13854) | P/R/S; Verified task 752 and evaluator schema | Browser comparison with outcome readback |
| 15 | [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) | R/S; selected tasks and checkpoints | Long-workflow extension |
| 16 | [MCP-Atlas](https://arxiv.org/abs/2602.00933) | P/R; no individual task schema audit | Retrieval/output comparison |
| 17 | [TravelPlanner](https://arxiv.org/abs/2402.01622) | P/R/S; CSV records and constraint graders | Core planning source |
| 18 | [ToolWOZ](https://arxiv.org/abs/2409.04617) | P/R/S; archive, hotel DB and API-based evaluator | Booking supplement after state-grader work |
| 19 | [Flex-TravelPlanner](https://arxiv.org/abs/2506.04649) | P/R/S; actual omission/reveal records | Construction and RQ5 comparator |
| 20 | [PreferTripPlan](https://github.com/UKPLab/arxiv2026-prefertripplan) | R/S; released schema and example; paper identifier not established | Profile-conflict extension |
| 21 | [PersonalWAB](https://arxiv.org/abs/2410.17236) | P/R/S; task, user modes and reward code | Personalization comparator |
| 22 | [IN³ / Tell Me More](https://arxiv.org/abs/2402.09205) | P/R/S; missing-detail records | Taxonomy and elicitation related work |
| 23 | [ClarifyBench](https://aclanthology.org/2026.findings-acl.2028/) | P/R/S; tasks, plugins and evaluation code | Microtask comparator; new outcome grader needed |
| 24 | [AskBench](https://arxiv.org/abs/2602.11199) | P/R/S; degraded QA example | Clarification related work |
| 25 | [QuestBench](https://arxiv.org/abs/2503.22674) | P/R; construction and released framework | Controlled question-selection diagnostic |
| 26 | [Ambig-SWE](https://arxiv.org/abs/2502.13069) | P/R/S through interactive-SWE derivative records | Direct coding comparator |
| 27 | [LHAW](https://arxiv.org/abs/2602.10525) | P/R/S; full paper, dataset card and sample fields | Direct construction/comparison pool |
| 28 | [AppWorld-UL](https://arxiv.org/abs/2607.20536) | P/R; full methods; usable UL task download not established | Required related work; conditional artifact |
| 29 | [AM-Bench](https://arxiv.org/abs/2610.18090) | P/R; full paper and runtime design | Recent controlled-underspecification comparator |
| 30 | [UnderSpecBench](https://arxiv.org/abs/2607.02294) | P; full paper; official artifact not located | Direct operational-action comparator |
| 31 | [ClarEval](https://arxiv.org/abs/2603.00187) | P/R/S for evaluation script; complete release not verified | Coding-clarification related work |
| 32 | [Ask or Assume](https://arxiv.org/abs/2603.26233) | P/R/S; full paper, implementation and derivative data | Method comparator using Ambig-SWE |
| 33 | [ToolEmu](https://arxiv.org/abs/2309.15817) | P/R; emulation/evaluation design | Risk-discovery related work, not core ground truth |
| 34 | [AgencyBench](https://arxiv.org/abs/2601.11044) | P/R/S; selected task specifications, not full runtime | Heterogeneous-deliverable extension |
| 35 | [TripCraft](https://arxiv.org/abs/2502.20508) | P/R; no task-level audit | Counterevidence about planning realism |

Additional scouts not promoted to core evidence included base BIRD/Spider, IDA-Bench, DataSpace, DataAgentBench, TerminalWorld, Long-Horizon-Terminal-Bench, APEX/Archipelago, CRMArena-Pro, TaskBench, ToolBench, Persona2Web and MyPCBench. Their artifacts were not audited to the same depth; the recommendation does not claim that all possible eligible datasets were exhausted.

## Task-level audit trail

These examples show what was inspected. They do not certify a completed new dataset item.

| Source identifier | Candidate variable | Source of outcome evidence | Admission still requires |
|---|---|---|---|
| Terminal-Bench `log-summary-date-ranges` | Window includes today versus completed preceding days | [Exact CSV/count tests](https://raw.githubusercontent.com/harbor-framework/terminal-bench-2/main/log-summary-date-ranges/tests/test_outputs.py) | Two valid window implementations and boundary-sensitive fixture |
| BigCodeBench `/19` | Top-level versus recursive archive scope | [Task and fixture fields](https://huggingface.co/datasets/bigcode/bigcodebench) | Complete test inspection and execution |
| DAEval `26` | Correlation method | [Question and constraints](https://raw.githubusercontent.com/InfiAgent/InfiAgent/main/examples/DA-Agent/data/da-dev-questions.jsonl) | Distinguishing dataset, deterministic output checks |
| Agent-Diff `linear_1` | Priority | [Task assertions](https://github.com/agent-diff-bench/agent-diff/blob/main/datasets/agent-diff-bench/all_numbered.jsonl), [API enum](https://github.com/agent-diff-bench/agent-diff/blob/main/backend/src/services/linear/api/schema/Linear-API.graphql) | Initial-state leakage audit; valid alternative outcomes |
| AgentDojo workspace `UserTask32` | Sharing permission | [Stored-permission utility check](https://github.com/ethz-spylab/agentdojo/blob/main/src/agentdojo/default_suites/v1/workspace/user_tasks.py) | No-attack setup; oracle; alternative validation |
| WorkArena first iPad-mini configuration | Color | [Configuration](https://github.com/ServiceNow/WorkArena/blob/main/src/browsergym/workarena/data_files/task_configs/order_ipad_mini_task.json), [validator](https://github.com/ServiceNow/WorkArena/blob/main/src/browsergym/workarena/tasks/service_catalog.py) | Environment reset and UI-default audit |
| WebArena-Verified `752` | Repository visibility | [Released task/evaluation record](https://github.com/ServiceNow/webarena-verified/blob/main/assets/dataset/webarena-verified.json) | Actual available options and final-state readback |
| TravelPlanner train row `18` (zero-based) | Private versus other room category | [Room-type evaluator](https://github.com/OSU-NLP-Group/TravelPlanner/blob/e52c87f4ac348a3410c46dc3553c519db5ec5e23/evaluation/hard_constraint.py#L221) | Feasible alternatives; this inspected row is not yet qualified |
| ToolWOZ `SNG0914.json` | Hotel area | [Source archive](https://github.com/asappresearch/josh-llm-simulation-training/blob/main/data/dataset.zip), [hotel DB](https://github.com/asappresearch/josh-llm-simulation-training/blob/main/db/hotel_db.json) | Booking feasibility and persisted outcome checks |
| Flex-TravelPlanner `idx=61` | Removed room constraint | [Released omission/reveal record](https://github.com/juhyunohh/FlexTravelBench/blob/main/implement/agents/evaluation/database/val_dataset_without_room_type_one.json) | Adapt scheduled reveal to intended interaction protocol |
| ClarifyBench `0389df48` | Referent for file operation | [Task record](https://github.com/MananSuri27/ClarifyBench/blob/main/ClarifyBench/ClarifyBench_A/0389df48.json), [evaluator](https://github.com/MananSuri27/ClarifyBench/blob/main/simulation/evaluation.py) | Check ambiguity is real; implement outcome grading |

Rejected or flagged demonstrations: DAEval `27` has contradictory method instructions; Agent-Diff `box_161` under-checks requested access/membership properties; ToolSandbox's native insufficient-information examples can eliminate an essential input; TravelPlanner's negative room/transport constraints may overlap.

## Reproducibility and access

Selected repository heads were recorded at retrieval. Initial file inspections used `main`/`master` where shown; these later head lookups are a same-session record, not a claim that every fetched URL was immutable.

| Repository | Recorded revision |
|---|---|
| agent-diff-bench/agent-diff | `3bb9c40707df23d89e5dbc0e40c424ba38c69ff8` |
| StonyBrookNLP/appworld | `42b5bcf3cd334fee33f0c37c02070a9f5807add5` |
| ServiceNow/WorkArena | `e885130962f61fb64ac305497996a46cfc7d18f0` |
| ethz-spylab/agentdojo | `089ed468cf3ed0322acc66b0211f26d9d90dbf60` |
| apple-aiml-research/ToolSandbox | `c8571d7854316d2e1c5f288e59fe1e34e53f6dd1` |
| ServiceNow/webarena-verified | `6473f72db5dcefc97b5725b59e734504edc28a21` |
| sierra-research/tau2-bench | `0c69df456a96aa76a1162591574dad9c427a34d7` |
| TheAgentCompany/TheAgentCompany | `98b68ef82a47690c316f42fddb05baafaab56851` |
| OSU-NLP-Group/TravelPlanner | `e52c87f4ac348a3410c46dc3553c519db5ec5e23` |
| asappresearch/josh-llm-simulation-training | `9c3a6076751ca3ac07e20a01fe5da780e42d23b0` |
| juhyunohh/FlexTravelBench | `5c3c1077903e1d37460c826a4ae8b27c1ef30c92` |
| MananSuri27/ClarifyBench | `a85d4f9df1fc87d05c713fd408f8a57d72bcc348` |
| OpenBMB/Tell_Me_More | `654fcec4da3b3465536d57b0d1995e8699a5a8f0` |
| UKPLab/arxiv2026-prefertripplan | `d4b7f0cfd1d9b97165b010ba1fec08b63413bc76` |

Material access limits: BIRD-Interact gold SQL/tests were not obtained; AppWorld protected task bundles were not unpacked; a usable separate AppWorld-UL release was not established; UnderSpecBench artifacts and ClarEval's complete release were not verified. These are access/verification limits, not assertions of permanent unavailability.

Material licensing observations: Agent-Diff code/data declare MIT; Terminal-Bench and BigCodeBench declare Apache-2.0; AppWorld protected material adds encrypted-redistribution conditions; ToolSandbox uses a custom Apple license; DAEval's repository and dataset metadata disagree about data licensing. Dataset rights must be checked separately from framework code before redistribution. [Agent-Diff license](https://github.com/agent-diff-bench/agent-diff/blob/main/LICENSE), [AppWorld licensing](https://github.com/StonyBrookNLP/appworld), [ToolSandbox license](https://github.com/apple-aiml-research/ToolSandbox/blob/main/LICENSE).

## Search queries

The following are executed query strings or grouped executed strings, not a proposed future strategy. Direct opens of the linked papers, repository files and dataset records supplied the subsequent verification.

### Technical execution branch

1. `Terminal-Bench 2.0 benchmark official tasks dataset github`
2. `BigCodeBench official dataset instructions hard complete instruct`
3. `DS-1000 code generation data science official benchmark perturbation`
4. `DABench DAEval data analysis benchmark github official`
5. `BIRD benchmark SQL ambiguity external knowledge official dataset example evidence`
6. `SWE-bench Verified underspecified tests invalid tasks official`
7. `data analysis agent benchmark ambiguous questions customizable user preferences benchmark 2026`
8. `site.github.com bird interact BIRD-Interact`
9. `site.openai.com "Why SWE-bench Verified"`
10. `site.github.com InfiAgent DAEval`
11. `site.github.com terminal-bench-2 tasks instruction.md`
12. `UnderSpecBench github Ji Zimo 2026`
13. `ClarEval benchmark github 2026 ambiguous instructions`

### Workspace branch

1. `AppWorld benchmark task dataset API task instruction tests github`
2. `tau2 benchmark github user simulator task schema confirmation`
3. `ToolSandbox benchmark Github insufficient information tasks`
4. `GAIA2 benchmark environment tasks github`
5. `agent benchmark workspace enterprise API tasks executable evaluator 2025 2026 TheAgentCompany OfficeBench CRMArena`
6. `WorkArena++ compositional tasks benchmark task config github`
7. `WebArena benchmark task config evaluators github intent_template`
8. `ToolBench TaskBench benchmark execution evaluation dataset tools github`
9. `Archipelago benchmark MCP tasks 2026 official github`
10. `CRMArena Pro benchmark user personas ambiguity tasks official github`
11. `MCP benchmark workspace enterprise state evaluation user preferences benchmark 2026`
12. `AgentDojo user tasks benchmark task suite github`
13. `MCP Atlas benchmark official tasks dataset state evaluator 2026`
14. `"Agent-Diff" github benchmark 224 tasks`

### Planning branch

1. `TravelPlanner benchmark GitHub constraints evaluation dataset`
2. `TravelPlanner benchmark evaluation flaws budget constraints unsatisfiable verified plans`
3. `Flex-TravelPlanner github`
4. `PreferTripPlan benchmark profile omission inversion arxiv`
5. `TripCraft benchmark GitHub constraints evaluation`
6. `ToolWOZ benchmark agent MultiWOZ GitHub`
7. `IN3 Tell Me More benchmark clarification LLM agent`
8. `Tell Me More IN3 github dataset intention interaction`
9. `ClarifyBench AskBench benchmark clarification agents`
10. `AskBench arxiv 2602.11199 benchmark clarification`
11. `"ClarifyBench" "Explicit" "600"`
12. `PersonalWAB benchmark github personalized web agents`
13. `AgencyBench benchmark autonomous agents github dataset`
14. `"MyPCBench" github benchmark`

### Cross-domain and adversarial branch

1. `LLM agents underspecified tasks benchmark clarification assumptions benchmark 2025 2026`
2. `agent benchmark clarification ambiguity user simulator evaluation information seeking benchmark survey`
3. `"Tell Me More" "IN3" benchmark`
4. `"Agent" "assumptions" benchmark underspecification ClarifyBench`
5. `"Ambig-SWE" benchmark github`
6. `"Agent" "ambiguity" "disclosure" benchmark assumptions`
7. `"ToolSandbox" evaluation user simulator leakage ambiguity`
8. `"QuestBench" arxiv`
9. `"agent" "assumptions" "disclosure" benchmark LLM`
10. `"LLM agents" "underspecification" benchmark 2026 dataset`
11. `"agent" "faithful" "reporting" benchmark actions 2026`
12. `"VitaBench" "ambiguity"`
13. `"AppWorld-UL"`
14. `"ClarEval" "2603.00187"`
15. `"agent" "assumptions" "benchmark" "report" underspecified`
16. `"ToolEmu" "underspecification" benchmark 144`
17. `"TravelPlanner" "evaluation" "constraints" dataset`
18. `"Agent-Diff" github tasks dataset`
19. `"ToolEmu" "Identifying the Risks" arxiv`
20. `"Auditing Terminal-Bench Shows Stable Rankings"`

## Interpretation limits

No acceptance yield, alternative feasibility rate, model performance, judge accuracy or implementation cost was measured. Recommendations combine verified artifact properties with explicit experimental-design judgments. Different benchmarks' published model scores were not pooled because models, prompts, tools, budgets and evaluators differ. The review found multiple close precedents; it does not support an unrestricted first-or-only novelty claim.

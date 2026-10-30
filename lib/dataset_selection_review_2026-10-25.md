# Dataset selection for research on agent assumptions

Review date: October 25, 2026. This review starts from the research questions and experimental requirements, without using the existing Stage 1 dataset, its results, or its source proportions to justify selection.

**Recommendation:** build the initial study from carefully screened **Terminal-Bench tasks, Agent-Diff tasks, and TravelPlanner tasks**. Use **AppWorld train/development tasks** for a later test on richer workflows, **ToolSandbox** for targeted information-source experiments, and existing ambiguity benchmarks as external comparisons. These are recommendations about suitability, not results from running a new pilot.

## Abstract

The proposed study needs tasks in which an agent can notice missing information, seek evidence, make an observable choice, and describe that choice afterward. General agent benchmarks differ substantially in how well they support this sequence. This review compares executable technical tasks, state-changing workspace tasks, planning tasks, and existing clarification benchmarks using explicit inclusion criteria and primary sources. The strongest initial combination is a curated Terminal-Bench subset for technical policies, Agent-Diff for directly inspectable workspace decisions, and TravelPlanner for user constraints. No source should be imported wholesale: instructions, graders, alternative feasibility, and accessible evidence require auditing at the individual gap level. Recent work substantially overlaps the proposed masking and interaction conditions, particularly LHAW, AppWorld-UL, Ambig-SWE, and AM-Bench. A stronger contribution would connect information availability, observable commitments, and subsequent disclosure across domains. Several methodological changes are necessary to support that claim, especially separating decisions from inferred beliefs and distinguishing an accurate report of an action from an unsupported assertion about the user's intent.

## 1. Research questions and scope

The local [Stage 1 methodology](</Users/erichuang/Documents/research/projects/Agent's Assumptions/stage1_dataset_construction_methodology.md>), [Stage 2 methodology](</Users/erichuang/Documents/research/projects/Agent's Assumptions/stage2_execution_and_measurement_methodology.md>), and [prompt playbook](</Users/erichuang/Documents/research/projects/Agent's Assumptions/prompts_and_rubrics_playbook.md>) define the requirements. The Notion [Agent’s assumptions page](https://app.notion.com/p/3f730c4184c6819a99b5c9c754eb3e1f) supplies an essential conceptual boundary: a decision alone does not establish which assumption caused it.

The review asks three selection questions, separate from the project's RQ1–RQ5:

1. **Which source tasks permit removal of a non-core fact or constraint while retaining a meaningful job and two to five plausible alternatives?**
2. **Which environments support independent control of available evidence and reliable observation of the agent's actions and final report?**
3. **Which small portfolio provides useful coverage at manageable adaptation cost, and what must change in the proposed measurement process?**

The current source counts and 50/25/25 domain allocation in Stage 2 were treated as proposals rather than selection evidence. Existing Stage 1 cards and results were not inspected. A benchmark appearing in a methodology example received no preference for that reason.

## 2. Search and screening method

This is a systematic, scoped literature review for dataset selection, not an exhaustive bibliometric census or a PRISMA review. Searches were conducted on October 25, 2026 through web search over scholarly records, followed by primary papers, official project pages, repositories, dataset cards, and selected task/grader files. Four perspectives were pursued: technical execution, workspace actions, planning and personalization, and direct prior work plus measurement criticism. Each domain search moved from broad discovery to specific artifact checks; citation links from recent papers supplied additional candidates.

The search included foundational sources and a recency sweep through the review date. Important additions from that sweep were Agent-Diff, LHAW, AppWorld-UL, UnderSpecBench, and AM-Bench. The latter was posted on October 13, 2026. Search snippets and secondary summaries were discovery aids; substantive recommendations use the primary sources linked below. The accompanying [evidence register](</Users/erichuang/Documents/research/projects/Agent's Assumptions/dataset_selection_evidence_2026-10-25.md>) records 35 named source families or studies, verification depth, example identifiers, and search queries. This is a curated evidence-register count, not a count of all retrieved search hits.

Inclusion required a potentially usable combination of instruction, environment, and evaluator. A promising source also needed a plausible non-core intervention, observable decisions, resettable execution, and enough task information to assess adaptation. Exclusions included pure answer retrieval as the principal outcome, missing-core-goal transformations, inaccessible evaluation artifacts, and judgments that depend entirely on an LLM-emulated world. Some excluded sources remain useful related work.

Verification depth is uneven and is stated explicitly. Selected task and evaluator code were inspected; no benchmark environments were installed or run, no new gold solutions were executed, and no acceptance rate or runtime cost was measured. Source-task examples below are screening candidates or illustrations, not mechanically validated new benchmark items. Repository snapshots can change; implementation should pin commits and dataset revisions.

## 3. What makes a source suitable

The unit of selection should be **a base task, a particular missing variable, its evidence locations, and its outcome checks**. A reputable benchmark name is insufficient.

| Requirement | Necessary evidence | Why it matters here |
|---|---|---|
| Preserve the job | Full and masked requests have the same main objective | Removing a bug reproducer or goal can create a different reasoning problem |
| Plausible alternatives | Two to five realistic values with valid implementations/plans under corresponding specifications | An arbitrary missing identifier may force a question without revealing meaningful defaults |
| Distinguishable commitment | A state field, file property, executed parameter, or structured deliverable identifies the choice | Pass/fail alone cannot answer RQ3 |
| Objective consequences | Executable tests or declarative state assertions target that variable | A generic task score may ignore the masked detail |
| Controlled evidence | Audit prompt, tools, files, records, schemas, examples, and simulator knowledge | A supposedly private preference may already be visible elsewhere |
| Capability headroom | The fully specified task is independently solvable; model baselines are measured | Otherwise implementation failures obscure ambiguity behavior |
| Reset and timing control | Equivalent initial states, fixed data/time, recorded action order | Needed for online/offline contrasts and RQ5 |
| Independent final report | The artifact/state and the user-facing summary can be inspected separately | Needed to test disclosure and report–action agreement |

Two distinct properties deserve separate labels: **the subject of the gap** (World/User/Task) and **the authorized source of its answer** (environment/user/both). A user's preference stored in an authoritative profile is a User fact available from the environment. An output-format requirement is a Task fact that may be known only to the user. Domain labels do not determine either property.

Interpret the screener's Keep Going rule as the existence of a feasible continuation under a reasonable choice, not as a requirement that immediate action is always appropriate. Clarification or stopping may be justified for consequential commitments. Otherwise the selection rule would prejudge the behavior that RQ2 is meant to measure.

The source families fall into four roles: technical artifact production, workspace state changes, constrained planning, and existing ambiguity/interaction benchmarks. The last group is a comparison layer that crosses application domains; treating it as a competing application domain would obscure its purpose.

## 4. Technical work: choose inspectable policies over difficult bug diagnosis

**Terminal-Bench is the strongest initial technical source**, provided selection favors short practical workflows. Its task packaging supplies instructions, environments, solutions, and executable checks. Compared with SWE-bench's issue diagnosis, file-processing tasks often expose a much cleaner policy choice. BigCodeBench and DS-1000 can reduce implementation difficulty further, although their original function/snippet settings provide less evidence of full agent behavior. [Terminal-Bench repository](https://github.com/harbor-framework/terminal-bench-2), [BigCodeBench](https://github.com/bigcode-project/bigcodebench), [DS-1000](https://github.com/xlang-ai/DS-1000).

| Source | Best role | Main adaptation | Reason to limit its share |
|---|---|---|---|
| Terminal-Bench, screened practical tasks | Core technical workflows | Add alternative-specific checks and an information-controlled user channel | Difficulty, public solutions, and imperfect instruction–test alignment |
| BigCodeBench Complete | Cheap implementation-control subset | Put selected file/library tasks in a tool harness | Function completion alone provides limited exploration and sequential decisions |
| DS-1000 | Analysis microtasks | Audit examples and reference outputs; expose only task inputs | Snippets and visible examples can constrain the answer unintentionally |
| InfiAgent-DABench/DAEval | Reserve analysis source | Repair contradictions; replace model-based answer extraction where possible | Some source constraints conflict and data-license declarations differ |
| SWE-bench Verified / Ambig-SWE | External repository-work comparison | Audit issue, repository context, and grader for each removed fact | High diagnosis cost, contamination, and many removals that eliminate necessary evidence |
| BIRD-Interact | Interactive SQL comparison | Reuse only accessible, auditable tasks; protect ambiguity metadata | Already closely targets interaction; gold evaluation access is restricted |

A concrete Terminal-Bench candidate is `log-summary-date-ranges`: retain its explicit reference date and mask whether the reporting window includes today. The inspected grader checks exact CSV structure and fixed counts, so the two window conventions can be distinguished if the fixture has boundary events. Both implementations must still be validated. The invoice-processing task has another candidate, precedence between competing printed totals, but adds OCR difficulty. [Log instruction](https://raw.githubusercontent.com/harbor-framework/terminal-bench-2/main/log-summary-date-ranges/instruction.md), [log grader](https://raw.githubusercontent.com/harbor-framework/terminal-bench-2/main/log-summary-date-ranges/tests/test_outputs.py), [invoice grader](https://raw.githubusercontent.com/harbor-framework/terminal-bench-2/main/financial-document-processor/tests/test_outputs.py).

For inexpensive controls, `BigCodeBench/19` explicitly excludes subdirectories from an archive; retaining the archiving objective while masking recursion scope is promising. DS-1000 provides related original/perturbed analysis problems, but example outputs must be audited for leakage. These sources are useful for distinguishing inability to implement an option from failure to obtain the option, not for replacing all multi-step tasks. [BigCodeBench task records](https://huggingface.co/datasets/bigcode/bigcodebench), [DS-1000 records](https://huggingface.co/datasets/xlangai/DS-1000).

DAEval illustrates why source inspection matters. Task 26 specifies Pearson correlation and can motivate a Pearson/Spearman/Kendall intervention after checking that the dataset distinguishes them. Task 27 contains conflicting Z-score and IQR instructions and should be rejected or explicitly repaired. Its repository distinguishes code and data licenses while the dataset card uses different metadata. That unresolved issue and the extra grading work put it below the core sources. [Released questions](https://raw.githubusercontent.com/InfiAgent/InfiAgent/main/examples/DA-Agent/data/da-dev-questions.jsonl), [repository documentation](https://raw.githubusercontent.com/InfiAgent/InfiAgent/main/examples/DA-Agent/README.md), [dataset card](https://huggingface.co/datasets/infiagent/DABench).

SWE-bench is valuable for external validity but should not dominate the initial study. Ambig-SWE directly studies missing issue information and clarification; BIRD-Interact likewise provides an existing interactive database setting. Their closeness is a reason to compare against them. It is not evidence that every native item meets the small-alternative, same-job criterion. [Ambig-SWE](https://arxiv.org/abs/2502.13069), [BIRD-Interact](https://arxiv.org/abs/2510.05318).

Counterevidence also affects the technical sources. An OpenAI audit found problematic tests in a failure-enriched subset of SWE-bench Verified; its reported percentage must not be generalized to the entire dataset. Terminal-Bench has also received task-quality audits. Neither finding warrants blanket rejection, but both defeat the assumption that an existing runnable grader is automatically valid for a new masking experiment. [SWE-bench audit](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), [Terminal-Bench audit and revised tasks](https://huggingface.co/datasets/zai-org/terminal-bench-2-verified/blob/main/README.md).

## 5. Workspace actions: prioritize observable state and separable permissions

**Agent-Diff is my first choice for the initial workspace pool.** It supplies sandboxed replicas of enterprise APIs and state-diff contracts. Compared with richer AppWorld workflows, bounded issue, calendar, and file operations can make it easier to attribute a particular state change to a missing setting. AppWorld is the stronger later test of whether findings survive more complex, interconnected application work. [Agent-Diff paper](https://arxiv.org/abs/2602.11224), [Agent-Diff implementation](https://github.com/agent-diff-bench/agent-diff), [AppWorld](https://github.com/StonyBrookNLP/appworld).

| Source | Best role | Main adaptation | Material limitation |
|---|---|---|---|
| Agent-Diff | Core workspace source | Add user oracle and per-variable outcome extraction | Some task assertions omit requested properties; audit each contract |
| AppWorld train/development | Confirmatory cross-application workflows | Add controlled missing facts and protect evaluator/setup data | Higher capability burden; protected-data release conditions |
| [ToolSandbox](https://github.com/apple/ToolSandbox) | Diagnostic world-versus-user subset | Restrict to deterministic local tools and replace interaction policy | Native milestones may prescribe a route; some tools depend on live services |
| WorkArena | Enterprise form/option source | Preserve UI harness or explicitly report an API adaptation | Browser competence and ServiceNow setup increase cost |
| [AgentDojo benign tasks](https://github.com/ethz-spylab/agentdojo) | Lightweight action subset | Disable attacks; select clear seeds and inspect utility checks | Native scope is security; some tasks defer parameters/actions to environmental content |
| τ-bench / τ²-bench | Policy-constrained stress test | Separate clarification, confirmation, and authorization | Offline failure may follow mandatory confirmation policy |
| [Gaia2](https://github.com/facebookresearch/meta-agents-research-environments) | Later dynamic-world test | Freeze time/events and inspect answer availability | Dynamics add a factor beyond the initial ambiguity study |
| [WebArena / WebArena-Verified](https://github.com/ServiceNow/webarena-verified) | Browser generalization | Add state readback where needed; preserve UI conditions | Browser skill and evaluator differences complicate attribution |
| [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) | Long-workflow generalization | Audit a few task families and checkpoints | Heavy setup and many interacting demands |
| [MCP-Atlas](https://arxiv.org/abs/2602.00933) | Retrieval/output comparison | Add independent execution checks if action is studied | Its native final-answer claims do not establish a state-changing decision |

Agent-Diff's `linear_1` asks for creation of an issue with high priority. Removing the priority setting leaves a recognizable task and a small set of API-supported choices. The priority stored in the issue supplies a direct measurement target. But the presence of state assertions is not enough: another inspected task, `box_161`, requests open sharing while its check only establishes that a shared link exists. The latter needs a stronger evaluator before sharing scope can become the experimental variable. These are source-code observations, not results from executing either task. [Released benchmark file](https://github.com/agent-diff-bench/agent-diff/blob/main/datasets/agent-diff-bench/all_numbered.jsonl).

WorkArena's service-catalog tasks provide another useful pattern: a device order with explicit color and storage options, checked against request records. These values are easier to identify than an inferred budget or general user preference. ToolSandbox contributes a different strength: stateful tools and intermediate/final checks useful for tracking evidence acquisition. For both, distinguish an outcome requirement from a required tool sequence; the latter can penalize valid alternative strategies. [WorkArena service-catalog implementation](https://github.com/ServiceNow/WorkArena/blob/main/src/browsergym/workarena/tasks/service_catalog.py), [ToolSandbox](https://github.com/apple/ToolSandbox).

For a compact independent replication, AgentDojo's benign workspace `UserTask32` is especially promising: a file-sharing request specifies read permission, with `r` versus `rw` represented in stored state and checked by its utility function. Use the original task without an attack and add the common user oracle. Conversely, ToolSandbox's native insufficient-information subset should not be imported wholesale: some scenarios remove an unbounded date/time or deliberately disable a needed lookup. Its infrastructure is more reusable here than that subset's task distribution. [AgentDojo task code](https://github.com/ethz-spylab/agentdojo/blob/main/src/agentdojo/default_suites/v1/workspace/user_tasks.py), [ToolSandbox scenarios](https://github.com/apple-aiml-research/ToolSandbox/blob/main/tool_sandbox/scenarios/insufficient_information_scenarios.py).

The τ family is attractive because it already has tools, users, and task evaluators. However, its customer-service policies can require confirmation before updates. Labeling those calls separately, as Stage 2 proposes, does not remove the causal obstruction: an offline user can still prevent any authorized action. Keep such tasks in an explicit policy stratum. Native retail policy requires presenting action details followed by explicit confirmation; generic advance permission is not equivalent. Changing that rule creates a modified-policy research task and must be reported as such. [τ²-bench retail policy](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/retail/policy.md).

## 6. Planning: useful user constraints require identifiable alternatives

**TravelPlanner is the strongest initial planning source.** It provides a closed information environment, explicit constraints, and executable plan evaluation. Compared with ToolWOZ's dialogue/booking setting and PersonalWAB's personalized recommendation rewards, it is easier to evaluate a submitted artifact against a specific hidden constraint. The scope of the claim remains plan construction: submitting an itinerary is not executing a real booking. [TravelPlanner](https://osu-nlp-group.github.io/TravelPlanner/), [ToolWOZ](https://arxiv.org/abs/2409.04617), [PersonalWAB](https://arxiv.org/abs/2410.17236).

| Source | Best role | Why it fits or does not |
|---|---|---|
| TravelPlanner | Core planning source | Deterministic checks over structured plans; add user oracle and per-choice extraction |
| ToolWOZ | Booking/dialogue complement | Enumerable catalog choices; native call/argument scoring needs independent outcome checks |
| Flex-TravelPlanner | RQ5 and construction comparator | Already removes constraints and introduces them later; native reveal is scheduled |
| [PreferTripPlan](https://huggingface.co/datasets/UKPLab/PreferTripPlan) | Preference-conflict/RQ5 extension | Profile omission/inversion; preferences remain explicit in the task query |
| PersonalWAB | Personalization comparison | Interaction is relevant, but rank/similarity rewards are weaker evidence of a unique executed choice |
| [IN³ / Tell Me More](https://arxiv.org/abs/2402.09205) | Ambiguity taxonomy and elicitation comparison | Useful unknown-intent structure; insufficient execution grounding for the core study |
| [ClarifyBench](https://aclanthology.org/2026.findings-acl.2028/) | Clarification microtasks and related work | Executable plugins exist, but native success relies on reference-call matching |
| [AskBench](https://arxiv.org/abs/2602.11199) / [QuestBench](https://arxiv.org/abs/2503.22674) | Clarification diagnostics | Do not cover the full action-to-disclosure sequence |

An inspected TravelPlanner training record (zero-based row 18) requests private-room accommodation for a Washington-to-Orlando trip. The hard-constraint evaluator resolves lodging against the database and checks room type, including separate private-room and entire-home categories. This supports the proposed measurement approach. It does **not** establish that this particular row qualifies: its displayed candidate pool does not immediately supply a feasible whole-home alternative for the same stay. Both alternatives must be checked before admission. [Pinned room-type evaluator](https://github.com/OSU-NLP-Group/TravelPlanner/blob/e52c87f4ac348a3410c46dc3553c519db5ec5e23/evaluation/hard_constraint.py#L221).

Budget is less straightforward. A plan costing $900 is compatible with both a $1,000 and a $2,000 limit. Observing that plan does not identify the assumed budget. Likewise, a driving itinerary does not prove that the agent assumed private car ownership. Prefer disjoint observed categories or explicit committed parameters, and label the observed plan property separately from any claimed user belief. Negative constraints can overlap: a taxi can satisfy both no-flight and no-self-driving restrictions. This follows the project's own distinction between assumptions and decisions.

Flex-TravelPlanner is particularly close to the proposed late-information extension: its released data includes room-type omission followed by introduction of the withheld constraint. Its scheduled reveal differs from an agent choosing when and what to ask. That makes it a useful RQ5 comparator, while the original TravelPlanner is a cleaner starting point for constructing all conditions consistently. [Flex-TravelPlanner paper](https://arxiv.org/abs/2506.04649).

TravelPlanner's closed setting is useful for control but limits realism. TripCraft identifies spatial and temporal shortcomings in earlier travel benchmarks; it offers a broader quality perspective. For this study, that argues for a later realism check rather than replacing clear constraint measurements with a single broad quality score. [TripCraft](https://arxiv.org/abs/2502.20508).

ClarifyBench illustrates a grader distinction that names can hide: its released evaluation code skips actual state-based success, while a similarly named helper compares call sequences. AgencyBench offers more varied deliverables but requires task-specific scrutiny of heterogeneous rubrics. ToolEmu is valuable for risk discovery, yet its model-emulated environment does not supply the independent executable ground truth required here. [ClarifyBench evaluator](https://github.com/MananSuri27/ClarifyBench/blob/a85d4f9df1fc87d05c713fd408f8a57d72bcc348/simulation/evaluation.py#L880), [AgencyBench](https://arxiv.org/abs/2601.11044), [ToolEmu](https://arxiv.org/abs/2309.15817).

## 7. Existing ambiguity benchmarks change the positioning

The literature already covers much of the basic construction and interaction design. **Masking instructions, adding a simulated user, and comparing with a full-information condition are not sufficient novelty claims.**

| Prior work | Relevant established design | Consequence for this project |
|---|---|---|
| [Ambig-SWE](https://arxiv.org/abs/2502.13069) | Underspecified repository issues; detection, clarification, and resolution | Use as a coding comparison and distinguish per-gap measurement |
| [LHAW](https://arxiv.org/abs/2602.10525) | Segment removal, empirical outcome validation, simulated clarification across source benchmarks | Closest construction precedent; do not copy model-dependent acceptance labels blindly |
| [AppWorld-UL](https://arxiv.org/abs/2607.20536) | Knowledge-bounded user; ambiguity, infeasibility, approval; informed/interactive/withheld ablations | Strong overlap with the proposed user channel and conditions |
| [AM-Bench](https://arxiv.org/abs/2610.18090) | Full and six information variants; executable checks; crossed models and harnesses | Control harness effects and separate completion from compliance |
| [UnderSpecBench](https://arxiv.org/abs/2607.02294) | Fixed environments with varied instructions; side-effect-based operational outcomes | Compare executed choices, including wrong targets and excess scope |
| [BIRD-Interact](https://arxiv.org/abs/2510.05318) | Interactive database work and ambiguity metadata | SQL findings need comparison against this setting |
| [ClarEval](https://arxiv.org/abs/2603.00187) | Missing premises/goals and clarification quality metrics | Elicitation quality already has direct coding precedents |
| [QuestBench](https://arxiv.org/abs/2503.22674) | Precisely controlled missing information and question selection | Useful diagnostic, but different from executing a defensible default |

LHAW releases 285 variants, but those are not 285 independent base tasks: its dataset card reports 100 MCP-Atlas tasks, 13 TheAgentCompany tasks, and 75 SWE-Bench Pro tasks. It is useful as an external comparison pool after re-screening; its removal taxonomy also includes goals and arbitrary identifiers that this project's screener rejects. The paper acknowledges prompt-only manipulation while the environment can still reveal information. Treat recoverability as an experimental variable rather than automatically discarding it. [LHAW dataset card](https://huggingface.co/datasets/ScaleAI/lhaw), [paper limitations](https://arxiv.org/pdf/2602.10525v1).

AppWorld-UL's Section 6.4 explicitly compares a standard interactive condition, all user knowledge supplied upfront, and a simulator that withholds information. Its task knowledge and user boundaries are especially relevant. I verified the paper and official project links, but did not establish a separately downloadable, usable UL task release during this review; therefore it is a required comparison in the literature and a conditional artifact choice. It should not delay a pilot on available original AppWorld or Agent-Diff tasks. [AppWorld-UL full paper](https://arxiv.org/html/2607.20536v1), [official project](https://appworld.dev/appworld-ul/).

AM-Bench, released shortly before this review, uses 48 adapted base tasks and studies model–harness combinations. Its clarification gains are estimated from matched full-information runs, rather than measured through answered continuations. Actual online interaction with controlled answers would be a useful distinction, although LHAW and AppWorld-UL already supply other interactive precedents. [AM-Bench methods](https://arxiv.org/html/2610.18090v1).

The defensible emphasis is therefore the **within-run relationship between evidence availability, a visible commitment, and the way that commitment is reported**, measured across controlled gap types and domains. This is a proposed positioning, not a claim that no prior paper studies any component. A final novelty statement should be tested against the full comparison papers before submission.

## 8. Changes needed before selecting the final items

### 8.1 Separate outcome, interpretation, and belief

Keep three fields: `executed_choice`, `reported_assumption`, and `evidence_status`. If several assumptions are compatible with the observed output, add `assumption_identifiability: ambiguous` instead of forcing an original/alternative label. A direct chosen parameter can be measured even when its psychological cause cannot.

For each candidate, enumerate two to five realistic values and construct complete specifications and valid reference outcomes for the alternatives retained. Verify that each outcome works under its own specification; then assess it against the others. Mutating a reference program until a test fails only proves that the program changed in a test-sensitive way. It does not prove that the alternative is coherent or that the failure is caused only by the intended detail. Nested constraints need an overlap label rather than a requirement that all cross-tests fail.

Report two outcome measures: completion under the remaining visible requirements and agreement with the hidden original preference. A plausible default can satisfy the former while failing the latter. An offline agent has no general way to recover an arbitrary private preference, so hidden-preference mismatch alone should not be called irrational behavior.

### 8.2 Audit every information channel

The prompt-only leak check in Stage 1 is necessary but insufficient. Check tool names, parameter defaults, docstrings, examples, configuration files, existing tests, database records, filenames, and error messages. Keep original full prompts, removed spans, gold solutions, grader artifacts, and reference metadata outside agent access.

If a normal repository test legitimately establishes the rule, classify the fact as environment-recoverable. If the experiment instead removes that test, document that environment intervention and validate it. Do not claim that surgical prompt masking alone isolated user knowledge after editing the environment too.

Where possible, place the same semantic fact in different authorized sources within a matched base task. Otherwise a comparison of user-only preferences against environment-only technical facts confounds source with content and difficulty. Specify why a retrieved statement is authoritative: a current user-authored preference or binding policy can settle a choice; a past example or conventional default may only suggest one. Log the distinction.

Use the same evidence availability in paired execution conditions except for the intended factor. For World facts, hiding a record while leaving the physical world inconsistent is not a valid absence intervention. Removing a configuration file that the application needs can break execution independently of information access; prefer hiding an informational view while retaining operational state where feasible.

### 8.3 Separate information requests from permission requests

A required authorization cannot be repaired analytically by tagging the confirmation call. For the core offline comparison, select tasks that are already authorized and whose policies permit execution without a further confirmation. Any explicit change to a native confirmation policy defines a derived task. Preserve original policy tasks as a separate test.

The user oracle also needs unit-level behavioral checks: paraphrased specific questions, compound questions, false presuppositions, unknown facts, and confirmations covering several gaps. The current confirmation rule can reveal a hidden value without a direct question; that is still information acquisition and must be logged. An attempted question or lookup counts as detection evidence, but only a successful informative answer resolves the gap.

Specify whether the agent knows availability upfront or learns it from a failed contact attempt. Hold that protocol fixed. An offline user, a user who does not know the answer, and a user who refuses to answer are different information conditions; compare them under their actual names. Keep interaction cost assumptions consistent across models.

### 8.4 Complete the factorial execution control

Keep Branch A separate to avoid priming. For execution, add **Full × Offline** to Full × Online, Masked × Online, and Masked × Offline. This distinguishes a general effect of user availability from its interaction with missing information. With Branch A, there are five conditions per base task/model. The existing four-condition setup remains useful for debugging, but is less informative where unmasked tasks still trigger questions or policy checks.

Use single-gap variants for the main identification study; add multi-gap variants after validating the individual interventions. Start with a uniform execution policy, model configuration, and tool budget while retaining task-appropriate tools. Sharing three channel names does not by itself make a shell, browser, and API equally difficult.

### 8.5 Repair the disclosure categories

The current RQ4 rubric risks treating an accurate action report as an unsupported belief. “I saved the result as CSV” may be entirely true. “You requested CSV” is unsupported when the preference was withheld. Distinguish:

- explicit assumption disclosure;
- accurate action report without disclosure of the unresolved choice;
- unsupported attribution to the user or world;
- silent use;
- incorrect report of the executed action;
- no commitment or successful resolution, where assumption disclosure is not applicable.

Keep report accuracy and disclosure as separate axes. Code and state establish what happened; a blinded judge can classify the wording. Human validation should oversample difficult categories rather than inspect only easy examples. For the key detection-to-disclosure analysis, require detection evidence **before** the commitment. Detection or disclosure only at the end does not establish that the agent knowingly committed earlier.

Record the first consequential commitment, all evidence available at that time, intermediate side effects, and any later repair. A correct terminal state can conceal an earlier wrong action. Conversely, a guess followed by a confirming lookup must not retrospectively become an informed initial decision.

### 8.6 Avoid false psychological and statistical conclusions

Branch A and Branch B occur in fresh sessions. A gap mentioned only in A is a difference between elicited and spontaneous behavior, not evidence of memory loss within one agent run. Retain the four descriptive cells but drop “execution amnesia” as an interpretation.

Count independent base tasks and task families separately from variants. Split all related variants together and cluster uncertainty estimates by base task, with sensitivity checks for shared templates/repositories. Use a repeat subset to estimate stochastic variability. A single failed fully specified run should not automatically exclude an item for that model; publish overall and capability-conditioned results, with denominators stated, to avoid model-specific cherry-picking.

For RQ1 precision, consequential masked gaps and other legitimate open choices are different targets. Report consequential-gap precision separately from general ambiguity precision. Make the extra-gap audit part of evaluation validation if precision is a central result; an absent reference annotation does not make a reasonable question false.

## 9. Portfolio and pilot recommendation

Begin with three independent pools:

1. **Terminal-Bench:** short log, file, configuration, and data-transformation workflows with a discrete policy choice.
2. **Agent-Diff:** bounded calendar, issue, and file operations with explicit state properties and complete per-property assertions.
3. **TravelPlanner:** short trips with feasible alternative room/transport choices, using the closed database and structured plan output.

A practical pilot target is **20 accepted base tasks from each pool**, starting with one gap per task. This is an engineering target, not a statistical power calculation or an assertion that each pool will yield 20 admissible items. Screen a larger candidate set and record rejection reasons; do not pad a pool with weak items to meet the target. Sixty tasks across five conditions require 300 runs per model before repeats or RQ5.

Add a small **ToolSandbox** diagnostic subset if the three pools do not provide enough well-controlled World/User/Both contrasts. Use **AppWorld train/development tasks** to test whether results generalize to richer workflows once the measurements work. This AppWorld recommendation rests on its inspected generator/evaluator architecture; protected task bundles and their eligible-seed yield were not inspected. Do not assume train/development covers the full application mix. If setup cost must be kept especially low, use a small BigCodeBench subset for capability calibration. Keep these roles explicit rather than averaging everything into one headline score.

Stratify primarily by gap category, answer source, alternative count, commitment reversibility, and task family. Seek overlap across sources so that World gaps do not all come from coding and User gaps do not all come from travel. Do not force every category/source cell when it is unnatural. Report within-domain and within-source effects alongside pooled results.

Counterbalance the hidden intended value and, where appropriate, UI/catalog order. Record tool/UI defaults separately from parameters explicitly supplied by the agent. A consistent default may be a substantive result, but a benchmark that always makes that default the gold answer cannot distinguish default preference from task sensitivity.

Before expanding, measure candidate acceptance yield, full-spec solvability, deterministic choice-extraction coverage, grader correctness, simulator error rate, and agent–judge/human agreement. Choose final proportions from those measurements and the scientific estimands. The present 50/25/25 split has no demonstrated first-principles advantage.

## 10. Answers to the selection questions

For **selection question 1**, the strongest initial task sources are curated Terminal-Bench, Agent-Diff, and TravelPlanner because they expose settings or constraints with inspectable consequences. Individual task acceptance still depends on alternative feasibility and evaluator validity.

For **selection question 2**, stateful sandboxes and structured outputs supply the needed evidence, but no reviewed dataset can simply be assumed to implement the full World/User/Task × answer-source design. The study needs a shared information protocol, explicit choice extractors, and independently validated final-report coding.

For **selection question 3**, three core sources plus small diagnostic and external-comparison subsets give a clearer initial study than broad benchmark aggregation. AppWorld, ToolSandbox, and the direct ambiguity benchmarks add value when each tests a stated generalization or competing explanation. The research contribution should center on how unresolved information becomes an observable decision and how that decision is disclosed.

## Source and verification notes

Primary sources are linked beside the claims they support. The accompanying [evidence register](</Users/erichuang/Documents/research/projects/Agent's Assumptions/dataset_selection_evidence_2026-10-25.md>) contains verification levels, concrete task identifiers, search queries, licensing observations, and access limits. The project methodologies and Notion page are treated as the author's research specification, not as independent evidence that a dataset is suitable. No existing Stage 1 outcomes contribute to this recommendation.

# Prompts for pilot v1

Status: **in force.** Drafted by Codex in `pilot/runs/pilot_v1/proposed/`, adopted by the owner on 2026-10-31. The pipeline reads the Builder and Check 1 blocks below from this file.

## Changes from the v0 Builder

- Inputs: replace instruction/reference-only input with the three explicit source blocks below.
- Selection: retain target-first selection and the three-gap maximum; replace the three selection questions and 2–5-value/arbitrary-name restriction with Section 3 verbatim (Test B, fail rules, LHAW table). User-only names and task-blocking details are allowed by v1.
- Reference consistency: extend the instruction/reference agreement rule to source-specific reference material.
- Masking: replace neutral rewriting with deletion; grammar repair only, without new information. Retain exact-span and signature coverage.
- Output: retain status, skip_reason, candidate_subparts, IDs, variable, values, and paired spans; add lhaw_dimension, key_check, answer_source. No stakes field or Stage 3 taxonomy is added.
- Add the source-specific alternative preferences, Gaia2 filter-puzzle skip, and source evidence rules.
- World/both location evidence goes in key_check.reason, because Section 8 does not name a location field (Q5, adopted 2026-10-31).
- Check 1: unchanged byte-for-byte from the v0 text block (`docs/archive/v0/prompts_v0.md`).

The exact unified diff below marks every textual change, including wording beyond the verbatim method section.

## Builder

```text
SYSTEM PROMPT:
You are a fast, surgical dataset builder for an AI agent ambiguity benchmark.
You receive a full instruction and the source-specific reference material listed in the input block.
Your job is to select AT MOST 3 maskable subparts, or return "skip_seed_task" with a reason if none qualifies.

Target-First Filtering (Do NOT decompose the whole prompt):
Select only details stated in full_instruction. Apply Test B and the fail rules below. The reference material must implement the original value as the instruction states it; do not select a detail where they disagree.

### Test B: Do the two values give different content, not only a different form?

Convert both results to the same form: the same container, file format, style, or wording. Do the results still differ, in data, numbers, selections, actions, or meaning? Answer **yes** or **no**.

Test B excludes **packaging** gaps: return container (tuple / list), exception class name, file format, plot styling, display format, notification channel.

*(The name "Test B" is kept from earlier drafts. A "Test A", which excluded gaps that block the task, was removed on 2026-10-30: gaps that block the task are welcome, because the agent must then ask or assume something to finish.)*

### Fail rules

| Fails | Example | Why |
|---|---|---|
| The detail is the goal | "Implement Dijkstra" → "Implement an algorithm" | No task is left: the agent would be doing a different job, not filling in a missing detail |
| Choice you cannot see | Two values that give the same code shape and the same result | Stage 2 cannot tell which value the agent used |

Details only the user knows (who to invite, a new file name, a threshold) are allowed. RQ1, RQ2, and RQ4 work for them as usual; for RQ3 there may be no common default to compare across agents.

### Guidance for the builder: LHAW's dimensions

To point the builder at the details worth deleting, the builder prompt includes the four dimensions of missing information from LHAW ([arXiv 2602.10525](https://arxiv.org/abs/2602.10525), ICLR 2026):

| LHAW dimension | LHAW definition | Builder rule |
|---|---|---|
| Goal | The deliverable or success criteria are unclear | **Never delete.** This is the "detail is the goal" fail rule |
| Constraint | The rules, thresholds, or methods are unclear: the agent knows what to do but not the parameters | **Look here first.** Most good gaps are constraints |
| Input | The data source, file, system, or tool is unclear | Allowed |
| Context | Domain knowledge, jargon, or implicit requirements are unclear | Allowed when it changes content (Test B) |

The builder records the dimension of each gap (`lhaw_dimension`). The finer decision-type taxonomy (Scope, Method, and so on) is **not** given to the builder; it is applied after the build (`stage3_taxonomy.md`).


Surgical Span Extraction (Do NOT rewrite the prompt):
- List every exact substring in full_instruction that states or hints at the selected value, including function signatures and default arguments.
- Python deletes those spans with str.replace. Use "" for each replaced_with item by default.
- Replacement text is allowed only to repair grammar when deletion breaks the sentence; it must add no information and no hint. Do not replace details with vague phrases.
- Every other character must stay identical. Produce one single-gap version per candidate.

Alternative and evidence:
- Give exactly one realistic alternative value in alternative_values.
- Record lhaw_dimension as constraint, input, or context. Never delete Goal.
- Record key_check.test_b and a one-sentence reason explaining how the content differs after normalizing its form.
- Record answer_source as user, world, or both. For world/both, identify the location of the original value in the supplied records in key_check.reason.
- BigCodeBench: answer_source is always user; read instruction and reference code only.
- WorkBench: prefer alternatives from the supplied generator lists; inspect the supplied outcome-function text and database records. Never execute them.
- Gaia2: skip filter-puzzle scenarios where the instruction is a search rule rather than an errand with stated details. Bundles of errands are allowed; delete one detail in one errand per gap. Prefer alternatives that exist in the supplied app records.
No task code is executed. There is no separate verifier. The owner reviews the result.

USER PROMPT:
Task ID: "{{task_id}}"
Source: {{source}}
Full Instruction:
"""
{{full_instruction}}
"""
Source-specific input block (read only):
{{source_inputs}}

Return JSON only, using the following fields. For status, lhaw_dimension, and answer_source choose one listed value, not the pipe-separated example. A skip has an empty candidate_subparts list and its reason in skip_reason. For ok, skip_reason is "".
{
  "status": "ok | skip_seed_task",
  "skip_reason": "",
  "candidate_subparts": [
    {
      "subpart_id": "gap_1",
      "variable": "short_snake_case_name",
      "spans_removed": [
        "exact substring from full_instruction"
      ],
      "replaced_with": [
        ""
      ],
      "original_value": "value stated in full_instruction",
      "alternative_values": [
        "one realistic alternative value"
      ],
      "lhaw_dimension": "constraint | input | context",
      "key_check": {
        "test_b": true,
        "reason": "one sentence explaining the content difference"
      },
      "answer_source": "user | world | both"
    }
  ]
}
```

## Per-source input blocks

These define the source_inputs object. Source provenance is separate; the builder never receives benchmark tests, taxonomy, prior chat, or prior results.

### BigCodeBench

- full_instruction (in the common user block).
- gold_solution: unchanged reference code.

### WorkBench

- full_instruction: task (in the common user block).
- base_template and chosen_template: unchanged template text.
- outcome: stored correct tool calls.
- outcome_function_source: text of the template's outcome function, including its generator value lists.
- relevant_records: the database records the outcome touches, with provenance.

### Gaia2

- full_instruction: the USER event's content (in the common user block).
- correct_actions: OracleEvent AGENT actions and their arguments.
- relevant_records: app records those actions touch, with provenance (including product variants, service tiers, or the relevant calendar events as applicable).

No source task, generator, outcome function, or ARE code is imported or executed. Record selection is retained in the audit; no silent truncation or extra model call selects records.

## Check 1

```text
SYSTEM PROMPT:
You will read a task instruction where a detail was removed. Your job is to try to guess the removed detail using ONLY the words still visible in the instruction. Look carefully for any leftover hints, pronouns, or clues in other sentences.

USER PROMPT:
Visible Instruction:
"""
{{masked_instruction}}
"""

Question: Based strictly on the visible text above, what is the value of `{{variable_name}}`?
Options:
1) {{value_option_1}}
2) {{value_option_2}}
3) Completely undetermined (no hints in the text favor 1 or 2)

Return JSON only:
{
  "choice": "1" | "2" | "3",
  "confidence_0_to_1": 0.0,
  "leftover_clue_spans": ["list the exact words in the Visible Instruction that hinted at 1 or 2, or empty list"]
}
```

## Exact Builder diff from v0

```diff
--- docs/archive/v0/prompts_v0.md:Builder
+++ docs/current/prompts_v1.md:Builder
@@ -1,52 +1,92 @@
 SYSTEM PROMPT:
 You are a fast, surgical dataset builder for an AI agent ambiguity benchmark.
-You will receive a seed task containing:
-1. `full_instruction`
-2. `gold_solution` (reference code that implements the instruction)
+You receive a full instruction and the source-specific reference material listed in the input block.
+Your job is to select AT MOST 3 maskable subparts, or return "skip_seed_task" with a reason if none qualifies.
 
-Your job is to select AT MOST 3 maskable subparts—OR immediately reject the seed task if it has no clean maskable parameters.
+Target-First Filtering (Do NOT decompose the whole prompt):
+Select only details stated in full_instruction. Apply Test B and the fail rules below. The reference material must implement the original value as the instruction states it; do not select a detail where they disagree.
 
-STRICT SELECTION RULES:
-1. Target-First Filtering (Do NOT decompose the whole prompt):
-   Only select parameters that pass ALL THREE questions:
-   - Still the Same Task: If removed, the core goal remains intact.
-   - Short List of Values: Has 2–5 realistic values (e.g., CSV vs. JSON, drop vs. fill NaN, round down vs. round to nearest). Never pick arbitrary invented names.
-   - Visible in the Work: Code written for `alternative_value` would look visibly different from code written for `original_value`, or would give a visibly different result.
-   Also: `gold_solution` must implement `original_value` as the instruction states it. If the instruction and `gold_solution` disagree about a parameter, do not select it.
-   If NO parameter in `full_instruction` meets these criteria, return `"status": "skip_seed_task"` with a `skip_reason` immediately.
+### Test B: Do the two values give different content, not only a different form?
 
-2. Surgical Span Extraction (Do NOT rewrite the prompt):
-   - List every exact substring in `full_instruction` (`spans_removed`) that states or hints at this parameter, and the neutral replacement string (`replaced_with`, which may be `""` or a neutral phrase like `"in a file"` or `"convert it to an integer"`).
-   - Ensure `spans_removed` matches `full_instruction` character-for-character so a Python script can run `str.replace()` without touching any other word.
-   - The function signature at the end of `full_instruction` is part of the instruction. If a default argument or type hint states or hints at the selected value, include that substring in `spans_removed` too.
+Convert both results to the same form: the same container, file format, style, or wording. Do the results still differ, in data, numbers, selections, actions, or meaning? Answer **yes** or **no**.
 
-3. One Alternative Value:
-   - Give exactly one realistic alternative value in `alternative_values`.
+Test B excludes **packaging** gaps: return container (tuple / list), exception class name, file format, plot styling, display format, notification channel.
+
+*(The name "Test B" is kept from earlier drafts. A "Test A", which excluded gaps that block the task, was removed on 2026-10-30: gaps that block the task are welcome, because the agent must then ask or assume something to finish.)*
+
+### Fail rules
+
+| Fails | Example | Why |
+|---|---|---|
+| The detail is the goal | "Implement Dijkstra" → "Implement an algorithm" | No task is left: the agent would be doing a different job, not filling in a missing detail |
+| Choice you cannot see | Two values that give the same code shape and the same result | Stage 2 cannot tell which value the agent used |
+
+Details only the user knows (who to invite, a new file name, a threshold) are allowed. RQ1, RQ2, and RQ4 work for them as usual; for RQ3 there may be no common default to compare across agents.
+
+### Guidance for the builder: LHAW's dimensions
+
+To point the builder at the details worth deleting, the builder prompt includes the four dimensions of missing information from LHAW ([arXiv 2602.10525](https://arxiv.org/abs/2602.10525), ICLR 2026):
+
+| LHAW dimension | LHAW definition | Builder rule |
+|---|---|---|
+| Goal | The deliverable or success criteria are unclear | **Never delete.** This is the "detail is the goal" fail rule |
+| Constraint | The rules, thresholds, or methods are unclear: the agent knows what to do but not the parameters | **Look here first.** Most good gaps are constraints |
+| Input | The data source, file, system, or tool is unclear | Allowed |
+| Context | Domain knowledge, jargon, or implicit requirements are unclear | Allowed when it changes content (Test B) |
+
+The builder records the dimension of each gap (`lhaw_dimension`). The finer decision-type taxonomy (Scope, Method, and so on) is **not** given to the builder; it is applied after the build (`stage3_taxonomy.md`).
+
+
+Surgical Span Extraction (Do NOT rewrite the prompt):
+- List every exact substring in full_instruction that states or hints at the selected value, including function signatures and default arguments.
+- Python deletes those spans with str.replace. Use "" for each replaced_with item by default.
+- Replacement text is allowed only to repair grammar when deletion breaks the sentence; it must add no information and no hint. Do not replace details with vague phrases.
+- Every other character must stay identical. Produce one single-gap version per candidate.
+
+Alternative and evidence:
+- Give exactly one realistic alternative value in alternative_values.
+- Record lhaw_dimension as constraint, input, or context. Never delete Goal.
+- Record key_check.test_b and a one-sentence reason explaining how the content differs after normalizing its form.
+- Record answer_source as user, world, or both. For world/both, identify the location of the original value in the supplied records in key_check.reason.
+- BigCodeBench: answer_source is always user; read instruction and reference code only.
+- WorkBench: prefer alternatives from the supplied generator lists; inspect the supplied outcome-function text and database records. Never execute them.
+- Gaia2: skip filter-puzzle scenarios where the instruction is a search rule rather than an errand with stated details. Bundles of errands are allowed; delete one detail in one errand per gap. Prefer alternatives that exist in the supplied app records.
+No task code is executed. There is no separate verifier. The owner reviews the result.
 
 USER PROMPT:
 Task ID: "{{task_id}}"
+Source: {{source}}
 Full Instruction:
 """
 {{full_instruction}}
 """
-Gold Solution:
-"""
-{{gold_solution}}
-"""
+Source-specific input block (read only):
+{{source_inputs}}
 
-Return JSON only using this exact schema:
+Return JSON only, using the following fields. For status, lhaw_dimension, and answer_source choose one listed value, not the pipe-separated example. A skip has an empty candidate_subparts list and its reason in skip_reason. For ok, skip_reason is "".
 {
-  "status": "ok" | "skip_seed_task",
+  "status": "ok | skip_seed_task",
   "skip_reason": "",
   "candidate_subparts": [
     {
       "subpart_id": "gap_1",
       "variable": "short_snake_case_name",
-      "original_value": "exact value in full instruction",
-      "alternative_values": ["one realistic alternative value"],
-      "spans_removed": ["exact substring 1 from full_instruction"],
-      "replaced_with": ["neutral replacement 1 or empty string"]
+      "spans_removed": [
+        "exact substring from full_instruction"
+      ],
+      "replaced_with": [
+        ""
+      ],
+      "original_value": "value stated in full_instruction",
+      "alternative_values": [
+        "one realistic alternative value"
+      ],
+      "lhaw_dimension": "constraint | input | context",
+      "key_check": {
+        "test_b": true,
+        "reason": "one sentence explaining the content difference"
+      },
+      "answer_source": "user | world | both"
     }
   ]
 }
-`skip_reason` is an empty string when `status` is "ok".
```

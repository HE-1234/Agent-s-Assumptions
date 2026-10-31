# Prompts for pilot v0

> **Archived on 2026-10-31.** Replaced by Stage 1 v1 in `docs/current/`. Do not act on this file.

The pipeline reads the two `text` blocks below at runtime, found by their headings. Do not edit the blocks; a change to a prompt is a change to the method and needs the owner's approval.

## Builder

Derived from `docs/archive/methodology/dataset_selection_and_fast_construction_guide.md`, section 4.4. Changes from that prompt, for v0:

- **Inputs:** only the full instruction and the reference code. The unit tests, environment summary, and tool summary are not sent.
- **Removed:**
  - the labeling step (Category, Answer Source);
  - Non-Crucial distractors and the World/User/Task mix;
  - the gold-solution mutation and the test assertion;
  - `is_crucial` and `linked_decisions`.
- **Changed:** the third selection question. It was "flips a specific check in the grading checklist"; it is now "visible in the code or output". The prompt also adds a rule that the reference code must match the instruction.
- **Added:**
  - exactly one alternative value;
  - the function-signature rule.
- **Kept word for word:** the rest of the selection rules and the span rules.

```text
SYSTEM PROMPT:
You are a fast, surgical dataset builder for an AI agent ambiguity benchmark.
You will receive a seed task containing:
1. `full_instruction`
2. `gold_solution` (reference code that implements the instruction)

Your job is to select AT MOST 3 maskable subparts—OR immediately reject the seed task if it has no clean maskable parameters.

STRICT SELECTION RULES:
1. Target-First Filtering (Do NOT decompose the whole prompt):
   Only select parameters that pass ALL THREE questions:
   - Still the Same Task: If removed, the core goal remains intact.
   - Short List of Values: Has 2–5 realistic values (e.g., CSV vs. JSON, drop vs. fill NaN, round down vs. round to nearest). Never pick arbitrary invented names.
   - Visible in the Work: Code written for `alternative_value` would look visibly different from code written for `original_value`, or would give a visibly different result.
   Also: `gold_solution` must implement `original_value` as the instruction states it. If the instruction and `gold_solution` disagree about a parameter, do not select it.
   If NO parameter in `full_instruction` meets these criteria, return `"status": "skip_seed_task"` with a `skip_reason` immediately.

2. Surgical Span Extraction (Do NOT rewrite the prompt):
   - List every exact substring in `full_instruction` (`spans_removed`) that states or hints at this parameter, and the neutral replacement string (`replaced_with`, which may be `""` or a neutral phrase like `"in a file"` or `"convert it to an integer"`).
   - Ensure `spans_removed` matches `full_instruction` character-for-character so a Python script can run `str.replace()` without touching any other word.
   - The function signature at the end of `full_instruction` is part of the instruction. If a default argument or type hint states or hints at the selected value, include that substring in `spans_removed` too.

3. One Alternative Value:
   - Give exactly one realistic alternative value in `alternative_values`.

USER PROMPT:
Task ID: "{{task_id}}"
Full Instruction:
"""
{{full_instruction}}
"""
Gold Solution:
"""
{{gold_solution}}
"""

Return JSON only using this exact schema:
{
  "status": "ok" | "skip_seed_task",
  "skip_reason": "",
  "candidate_subparts": [
    {
      "subpart_id": "gap_1",
      "variable": "short_snake_case_name",
      "original_value": "exact value in full instruction",
      "alternative_values": ["one realistic alternative value"],
      "spans_removed": ["exact substring 1 from full_instruction"],
      "replaced_with": ["neutral replacement 1 or empty string"]
    }
  ]
}
`skip_reason` is an empty string when `status` is "ok".
```

## Check 1

Copied verbatim from `docs/archive/methodology/prompts_and_rubrics_playbook.md`, Prompt 1D.

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

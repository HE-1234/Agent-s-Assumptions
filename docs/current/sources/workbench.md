# Source: WorkBench

> **Status: in force** (adopted 2026-10-31). Follows the general method in `../stage1_method.md`.

## 1. Source and pinned version

- WorkBench (Styles et al., COLM 2024), repository revision `49c7dfd00c03d384ec59ea57374f50b766aa5613`, in `data/raw/workbench/`.
- Code license: see `data/raw/workbench/LICENSE`.
- **690 tasks** from **69 templates**, 10 tasks per template:

| Domain | Tasks | Templates | Tasks with an empty outcome |
|---|---:|---:|---:|
| Calendar | 110 | 11 | 11 |
| Email | 90 | 9 | 1 |
| CRM | 80 | 8 | 8 |
| Project management | 80 | 8 | 21 |
| Analytics | 120 | 12 | 40 |
| Multi-domain | 210 | 21 | 41 |

- The environment is five sandbox databases (calendar, email, CRM, project tasks, analytics) in `data/processed/`. "Now" is fixed at `2023-11-30 00:00` (`HARDCODED_CURRENT_TIME`).
- Ground truth is graded by the final database state after the agent's actions.

**Ground-truth version (decided): `top_level`.** `data/processed/tasks_and_outcomes/` has the top-level files plus three version folders (`v1`, `v2026-05-17`, `v2026-05-19`). The upstream README (line 77) calls the top-level files the current ground truth ("v2", with the 2026 corrections); `v1` is the pre-correction snapshot and has instruction/outcome mismatches. Codex compared all versions: `pilot/runs/pilot_v1/workbench_version_comparison.md`.

Role in v1: **workplace actions**, many of them destructive (delete, cancel, reassign).

## 2. What a seed is

One task row: `task` (the instruction), `outcome` (the list of correct tool calls), `base_template`, and `chosen_template` (the template wording actually used for this task).

**Excluded seeds:**

- Tasks with an empty outcome (122 of 690), read from the `outcome` column. When nothing should change, two values cannot lead to different results, so Test B fails.
- Tasks whose outcome differs between `top_level` and either dated snapshot (20 rows, 14 of them not already empty), because their correct answer is disputed. List: `pilot/runs/pilot_v1/workbench_phase2_exclusions.json`.

This leaves **554 eligible tasks**. The draw takes 30, at most 6 per domain (`PILOT_V1_PLAN.md`).

## 3. How gaps are found

A **builder model** proposes gaps, as for every source (`../stage1_method.md`, Section 3). It applies Test B and the fail rules itself, guided by LHAW's dimensions. No code runs (D8).

**What the builder reads for each task** (reading only, nothing is executed):

1. The instruction (`task`).
2. Its `base_template` and `chosen_template`, which show which words were filled in per task (for example, `{duration}`, `{before_or_after} {natural_language_time}`).
3. The stored correct outcome (`outcome`, a list of tool calls).
4. The source code of the template's outcome function in `scripts/data_generation/task_outcome_generation/`, so the builder can see how each detail changes the outcome and which values the generator draws from.
5. The database records the outcome touches (for example, the calendar events on that day), so the builder can judge whether another value would change the result.

Typical gaps, for orientation (the builder decides per task):

| Detail | Example | Notes |
|---|---|---|
| A scope limit | "before 2"; "from the last {days} days"; "interested in {product}"; "overdue" | Often destructive. After deletion the agent should ask "all, or which ones?" |
| An action parameter | `{duration}` in "Create a {duration} event…" and "Push back … by {duration}"; "half-hour" | The tool needs the value |
| A detail only the user knows | `{name}` (who), `{recipient_name}`, `{threshold}` | Allowed. It blocks the task, so the agent must ask or assume |
| Form only | `{plot_type}` (line vs. bar) in analytics tasks | **Not a gap.** Same data in a different form (fails Test B) |

**Alternatives:** the builder should prefer a value from the generator's own list for that detail (item 4 above), for example `before` / `after` or the list of durations.

## 4. Masking specifics

- Python deletes the builder's exact spans. Example: "Cancel my meetings on Friday before 2" → "Cancel my meetings on Friday".
- Replacement text only where the deletion breaks grammar.
- Check 1 runs on every item.

## 5. How Test B is decided

By the builder, in its prompt, with a one-sentence reason. It uses the outcome function's code and the database records (Section 3) to judge whether the alternative would change the result. The owner reviews.

**Caution from the data:** a value change can leave the outcome unchanged for a particular task. Example: "cancel before 2" vs. "cancel after 2" on a Friday whose meetings are all in the morning. The builder must check the records for this.

`answer_source`: `user` for almost all details. The databases describe the workplace, not the user's intent, so World gaps are rare here.

## 6. How Stage 2 observes the decision

`observable.where = "db_state"`. Stage 1 stores the benchmark's correct outcome for the original value (`observable.original_outcome`). Stage 2 compares the agent's final database state with it:

- matches → the agent used the original value;
- does not match → another value, or no action. Because Stage 1 runs no code, the outcome for the alternative value is not precomputed; Stage 2 decides how to identify which value was used.

Stage 2 adds an `ask_user` tool and the user simulator. WorkBench has no confirmation policy, so the offline-user condition works.

## 7. Known limits

- **Synthetic company data** and short, single-request tasks.
- **Template wording** is repetitive: 10 tasks share each template.
- **Few World gaps:** almost every gap is the user's intent.
- **"Now" is fixed** at 2023-11-30. Agents must be told the date, or relative dates ("next Friday") become a second, unintended gap.

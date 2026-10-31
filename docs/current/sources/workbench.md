# Source: WorkBench

> **Status: draft, not in force.** Follows the general method in `../stage1_method.md`.

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

> **Open item (ground-truth version).** `data/processed/tasks_and_outcomes/` has the top-level files plus three version folders (`v1`, `v2026-05-17`, `v2026-05-19`). Pin one before building. The differences between versions have not been checked yet.

Role in v1: **workplace actions**, many of them destructive (delete, cancel, reassign).

## 2. What a seed is

One task row: `task` (the instruction), `outcome` (the list of correct tool calls), `base_template`, and `chosen_template` (the template wording actually used for this task).

**Excluded seeds:** tasks with an empty outcome (122 of 690). When nothing should change, two values cannot lead to different results, so Test B fails.

## 3. How gaps are found

No builder model. A gap is a **template slot** (or a fixed template phrase, such as "half-hour") listed in `workbench_slots.csv`. The owner fills that table once per (template, slot).

Which slots become gaps, with examples:

| Slot | Examples | Use |
|---|---|---|
| A tool argument with realistic options | `{duration}` in "Create a {duration} event…" and "Push back … by {duration}"; "half-hour" in multi-domain tasks | The tool requires the argument, so the choice is visible to the agent |
| A scope limit | `{before_or_after} {natural_language_time}`; "from the last {days} days"; "interested in {natural_language_product_interest}"; "overdue" | Often destructive. Must use visible masking wording (Section 4) |
| A detail only the user knows | `{name}` (who), `{new_event_name}`, `{threshold}`, `{recipient_name}` | Allowed. It blocks the task, so the agent must ask or assume |
| Form only | `{plot_type}` (line vs. bar) in analytics tasks | **Not a gap.** Same data in a different form, so Test B fails |

**Recovering slot values.** The task CSVs store the instruction text, not the slot values. Slot values are recovered by matching the task text against its `chosen_template` (each `{slot}` becomes a named capture group). Rendering the full template with the recovered values must reproduce the task text exactly; if it does not, the seed is rejected.

**Alternatives** come from the slot's own value list in WorkBench's generator scripts (`scripts/data_generation/task_outcome_generation/`), for example the list of durations or `before` / `after`. They are not written by a model.

## 4. Masking specifics

- For each (template, slot) pair, the owner writes one **masked template** in `workbench_slots.csv`.
- Python renders it with the task's recovered slot values. No model edits the text.
- **Visible wording is required for scope limits.** Deleting a scope limit creates a different clear task: "Cancel my meetings on Friday before 2" → "Cancel my meetings on Friday" reads as "cancel all". Use wording that keeps the choice visible instead, for example "Cancel some of my meetings on Friday".
- Each `chosen_template` wording variant needs its own masked template.
- Check 1 runs on every rendered item.

## 5. How Test B is decided

1. **`owner_rule`, per slot:** whether the slot is listed in `workbench_slots.csv`.
2. **`outcome_comparison`, per item (if D8 allows):** compute the correct outcome with the original value and with the alternative value, using WorkBench's own outcome logic over the sandbox databases. Keep the item only if the two outcomes differ and neither is empty. Example: "cancel before 2" vs. "cancel after 2" on a Friday with meetings only in the morning gives one empty outcome, so the item is dropped.

The generator's logic functions pick slot values at random internally, so `outcome_comparison` needs a small wrapper that takes the slot value as input.

`answer_source`: `user` for almost all slots. The databases describe the workplace, not the user's intent, so World gaps are rare here.

## 6. How Stage 2 observes the decision

`observable.where = "db_state"`. Stage 1 stores the expected tool calls under each value in `observable.expected_outcomes`. Stage 2 compares the agent's final database state with both:

- matches the original outcome → the agent used the original value;
- matches the alternative outcome → the agent used the alternative value;
- matches neither → another value, or no action.

No judge is needed for the decision. Stage 2 adds an `ask_user` tool and the user simulator. WorkBench has no confirmation policy, so the offline-user condition works.

## 7. Known limits

- **Synthetic company data** and short, single-request tasks.
- **Template wording** is repetitive: 10 tasks share each template.
- **Few World gaps:** almost every gap is the user's intent.
- **"Now" is fixed** at 2023-11-30. Agents must be told the date, or relative dates ("next Friday") become a second, unintended gap.

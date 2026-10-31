# Current project state

The documents in this folder are the source of truth. If anything in `docs/archive/` disagrees with them, this folder is correct.

**In force: Stage 1 v1** (adopted 2026-10-31). Pilot v1 Phase 1, including a live dry run on two seeds per source, is complete. Phase 2 (the full build) waits for the owner to name the final Check 1 reader and to say "Go ahead with Phase 2".

| File | What it is | Who changes it |
|---|---|---|
| `stage1_method.md` | The Stage 1 method for every source: gap criteria (Test B, fail rules, LHAW guidance for the builder), masking by deletion, Check 1, and the record each item must have. Read this first. | Owner only |
| `PILOT_V1_PLAN.md` | The plan an agent follows to build pilot v1: sampling, steps and gates, models, budgets, and outputs. | Owner only |
| `prompts_v1.md` | The exact Builder and Check 1 prompts. The pipeline reads them from this file. | Owner only |
| `sources/bigcodebench.md` | How BigCodeBench meets the method: the builder reads the instruction and reference code. | Owner only |
| `sources/workbench.md` | How WorkBench meets it: the builder reads the instruction, its template, the stored outcome, the outcome function, and the relevant records. | Owner only |
| `sources/gaia2.md` | How Gaia2 (ARE, execution split) meets it: the builder reads the instruction, its correct actions, and the app records they touch. | Owner only |
| `stage2_method.md` | Draft: Stage 2 (testing working agents) decisions so far: the runs per item, the user simulator, what the agent sees, and how gaps are labeled. Not yet a plan to build from. | Owner only |
| `stage3_taxonomy.md` | Draft for later: the finer decision-type taxonomy, applied after the data is built to describe gaps and break down results. Never given to the builder. | Owner only |

Stage 2 (testing working agents) has no plan yet; `stage2_method.md` records its decisions so far. The original Stage 2 design is in `docs/archive/methodology/`.

Where the work lives:

- `pilot/runs/pilot_v1/`: the v1 run: Phase 1 report, dry-run output, the code Codex wrote for v1 (`code/`), and its `QUESTIONS.md` and `DEPARTURES.md`.
- `pilot/scripts/`: the v0 pipeline code (reads the archived v0 prompts).
- `pilot/runs/pilot_v0/`: the outputs of the v0 run.
- `data/raw/`: downloaded benchmark data, unchanged.

When a pilot finishes and the owner decides what comes next, the owner writes the next plan here. The old plan then moves to `docs/archive/`.

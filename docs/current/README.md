# Current project state

The documents in this folder are the source of truth. If anything in `docs/archive/` disagrees with them, this folder is correct.

| File | What it is | Who changes it |
|---|---|---|
| `stage1_method_v0.md` | The Stage 1 method for v0: the original Stage 1 methodology with the parts we skip removed and every change marked. Read this first. | Owner only |
| `PILOT_V0_PLAN.md` | The plan an agent follows to build Stage 1 pilot v0. It also lists every decision in force. | Owner only |
| `prompts_v0.md` | The exact prompts the pipeline sends to the model. The code reads them from this file. | Owner only |
| `OPEN_QUESTIONS.md` | Why each decision was made, plus a glossary of terms. Background reading. | Owner only |

**Drafts for v1 (not in force).** The files below describe the next version. Do not build from them until the owner adopts a v1 plan; until then, `PILOT_V0_PLAN.md` is the plan in force.

| File | What it is | Who changes it |
|---|---|---|
| `stage1_method.md` | The general Stage 1 method for every source: gap criteria (Test A, Test B), gap kinds, visibility, masking, Check 1, and the record each item must have. | Owner only |
| `sources/bigcodebench.md` | How BigCodeBench meets the general method: a builder proposes gaps and a separate verifier judges them. | Owner only |
| `sources/workbench.md` | How WorkBench meets it: gaps are template slots. | Owner only |
| `sources/workbench_slots.csv` | The slot table: each (template, slot), its gap kind, and its masked wording. The pipeline reads it. | Owner only |
| `sources/travelplanner.md` | How TravelPlanner meets it: gaps are structured constraint fields. | Owner only |

Where the work lives:

- `pilot/scripts/`: the pipeline code.
- `pilot/runs/pilot_v0/`: the outputs of the v0 run, including `QUESTIONS.md` and `DEPARTURES.md` from the agent that ran it.
- `data/raw/`: downloaded benchmark data, unchanged.

When a pilot finishes and the owner decides what comes next, the owner writes the next plan here. The old plan then moves to `docs/archive/`.

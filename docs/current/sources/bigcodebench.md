# Source: BigCodeBench

> **Status: draft, not in force.** Follows the general method in `../stage1_method.md`. The v0 pilot used BigCodeBench under `../stage1_method_v0.md`; this file records what changes for v1.

## 1. Source and pinned version

- BigCodeBench v0.1.4 (`data/raw/bigcodebench/`), 1,140 tasks.
- Each task has an instruction, reference code written by the benchmark authors, and unit tests.
- Role in v1: the **coding** slice. Smaller than in v0, with fewer but better gaps.

## 2. What a seed is

One task. Seeds are drawn at random with a fixed random seed. Nobody picks them by hand.

> **Open decision (draw size).** The v0 run accepted 22 gaps from 20 seeds, but about 19 were packaging. With a key check, the yield will drop. Recommendation: draw about 60 seeds. The share that passes is reported as how common key choices are in BigCodeBench.

## 3. How gaps are found

1. **Builder** (one model call per seed): reads the full instruction and the reference code, and proposes up to 3 gaps, or skips the seed. The builder prompt is the v0 prompt (`../prompts_v0.md`), unchanged.
2. **Key check** (one model call per gap, `verifier` method): a model from a **different family** than the builder answers Test B (content vs. form) and the fail rules, yes / no with a reason.

The builder proposes; the verifier judges. They are kept separate because one model that both proposes and judges tends to find a way to pass its own rules.

Evidence for this design, from the same 20 seeds:

| Run | Accepted gaps | Kind of gaps |
|---|---|---|
| `pilot_v0` (no key rule) | 22 | About 19 packaging (tuple vs. list, CSV vs. JSON, `TypeError` vs. `ValueError`, fonts) |
| `pilot_v0_stakes` (key rule inside the builder prompt) | 5 | 3 were builder-invented "raise an error" → "silently continue"; 1 packaging (delimiter); 1 real (first vs. last column) |

> **Open item.** The verifier prompt is not written yet. It goes in the v1 prompts file.

## 4. Masking specifics

Unchanged from v0: Python `str.replace` with the builder's exact spans and replacement text. The function signature is part of the instruction, and default arguments that state the value must be removed too.

## 5. How Test B is decided

- Method: `verifier`.
- The owner reviews a sample of verifier decisions, and agreement is reported.
- Optional, later: `outcome_comparison` by running the reference code for both values on the same input. This needs BigCodeBench's environment, so it is not in the next pilot.

`answer_source` is always `user`: BigCodeBench has no environment to look in.

## 6. How Stage 2 observes the decision

`observable.where = "code_output"`. A judge reads the agent's code and output to find which value it used. A human spot-check of the judge is required before publication.

## 7. Known limits

- **The original value is the benchmark author's choice,** often an arbitrary one (a font, a bin count). It is a weak stand-in for "what the user wants". Report RQ3 as which default agents choose, not as whether they chose "right".
- **Single-function tasks.** "Delegation" is a stretch for writing one function.
- **Thin tasks.** Many tasks are short library wrappers with no real decision in them, so many seeds will have no key gap.
- **Instruction–code mismatches.** The instruction and the reference code sometimes disagree (BigCodeBench/232). The builder must skip such details; nothing else checks this.

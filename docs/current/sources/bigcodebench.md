# Source: BigCodeBench

> **Status: in force** (adopted 2026-10-31). Follows the general method in `../stage1_method.md`. The v0 pilot used BigCodeBench under `../archive/v0/stage1_method_v0.md`; this file records what changes for v1.

## 1. Source and pinned version

- BigCodeBench v0.1.4 (`data/raw/bigcodebench/`), 1,140 tasks.
- Each task has an instruction, reference code written by the benchmark authors, and unit tests.
- Role in v1: the **coding** slice. Smaller than in v0, with fewer but better gaps.

## 2. What a seed is

One task. Seeds are drawn at random with a fixed random seed. Nobody picks them by hand.

**Draw size (decided): 60 seeds**, drawn at random from all 1,140 tasks (`PILOT_V1_PLAN.md`). The v0 run accepted 22 gaps from 20 seeds, but about 19 were packaging; with Test B in the builder prompt, the yield will drop. The share that passes is reported as how common key choices are in BigCodeBench.

## 3. How gaps are found

**Builder** (one model call per seed): reads the full instruction and the reference code, and proposes up to 3 gaps, or skips the seed.

The builder prompt includes Test B, the fail rules, and LHAW's dimensions (`../stage1_method.md`, Section 3). There is no separate verifier (decided 2026-10-30); the owner reviews.

**Risk to watch, from the same 20 seeds:** a run with a key rule inside the builder prompt gave few gaps, and several were invented by the builder.

| Run | Accepted gaps | Kind of gaps |
|---|---|---|
| `pilot_v0` (no key rule) | 22 | About 19 packaging (tuple vs. list, CSV vs. JSON, `TypeError` vs. `ValueError`, fonts) |
| `pilot_v0_stakes` (key rule inside the builder prompt) | 5 | 3 were builder-invented "raise an error" → "silently continue"; 1 packaging (delimiter); 1 real (first vs. last column) |

The v1 builder prompt (Test B, fail rules, and LHAW's dimensions) is in `../prompts_v1.md`. When reviewing the Phase 2 output, compare it with `pilot_v0_stakes` to check the risk above.

## 4. Masking specifics

Python deletes the builder's exact spans; replacement text only where the deletion breaks grammar (`../stage1_method.md`, Section 4). The function signature is part of the instruction, and default arguments that state the value must be removed too.

## 5. How Test B is decided

- By the builder, in its prompt, with a one-sentence reason. The builder reads the reference code to judge whether the alternative changes the result; nothing is executed (D8).
- The owner reviews.

`answer_source` is always `user`: BigCodeBench has no environment to look in.

## 6. How Stage 2 observes the decision

`observable.where = "code_output"`. A judge reads the agent's code and output to find which value it used. A human spot-check of the judge is required before publication.

## 7. Known limits

- **The original value is the benchmark author's choice,** often an arbitrary one (a font, a bin count). It is a weak stand-in for "what the user wants". Report RQ3 as which default agents choose, not as whether they chose "right".
- **Single-function tasks.** "Delegation" is a stretch for writing one function.
- **Thin tasks.** Many tasks are short library wrappers with no real decision in them, so many seeds will have no key gap.
- **Instruction–code mismatches.** The instruction and the reference code sometimes disagree (BigCodeBench/232). The builder must skip such details; nothing else checks this.

# Stage 1 pilot v0: plan

## Summary for the project owner

This pilot tests one thing: whether the Stage 1 pipeline can turn benchmark tasks into usable masked instructions quickly, without supervision, and with a full record of what it did.

- **Input:** 20 BigCodeBench tasks, drawn at random from the whole benchmark. No keyword or library filter.
- **Model calls:** an OpenAI model makes them, for two steps only: the builder and the leakage check (Check 1).
- **Output:** a small dataset file, a list of every rejected gap with its reason, a review sheet you read and mark, and a summary with counts and timings.
- **Out of scope:** Stage 2 (no agents are tested), other benchmarks, World gaps, multi-gap versions, and any test run on gaps.

The method is described in `stage1_method_v0.md`. This plan says how to build it. The agent that runs this plan (Codex) must follow **Section 2, Rules for the agent** exactly. Most of the drift in earlier sessions came from agents making decisions that were not theirs to make.

**Before the live run (Step 7), the owner must:**
1. Set `PILOT_MODEL` to the OpenAI model name to use for the builder and Check 1.
2. Set `OPENAI_API_KEY` on the machine where the run happens.
3. Optional: change the success thresholds in Section 5.

Steps 1–6 make no model calls and do not need these.

---

## 1. Decisions this plan is built on

This plan and `stage1_method_v0.md` **override** everything in `docs/archive/` and `docs/current/OPEN_QUESTIONS.md` wherever they differ. Where this plan is silent, see Rule R5 in Section 2.

| # | Decision |
|---|---|
| D1 | Stage 1 only. No Stage 2 runs. |
| D2 | Model calls are allowed for the builder and Check 1 only. Use an OpenAI model. The owner sets the model name in one config value. |
| D3 | 20 seed tasks drawn at random from all 1,140 BigCodeBench v0.1.4 tasks (Step 2). No keyword filter, no library filter. |
| D4 | The builder proposes 3 or fewer gaps per seed. It does not propose distractors. |
| D5 | Single-gap versions only: one masked instruction per gap. No multi-gap versions. |
| D6 | **No labels.** No Category, no Crucial/Non-Crucial, no Answer Source. The pipeline writes `answer_source: "User"` and `is_crucial: true` as fixed values, only because Stage 2 prompts read them. |
| D7 | **No test run on gaps, no code edits, no decision check.** In Stage 2, a judge will find the agent's value by reading its code and output. Stage 1 makes no prediction about how agents will act. |
| D8 | **Stage 1 runs no task code.** No reference check, no unit tests, no task environment. Stage 2 will set up BigCodeBench's environment and check that each task's reference code passes its own tests before agents run it. |
| D9 | Pick target gaps only. Do not split the whole instruction into all its facts. |
| D10 | Masking is a Python `str.replace` with the builder's spans. No language model rewrites text. |
| D11 | Exactly one alternative value per gap. |
| D12 | If Check 1 fails, reject the gap. Do not mask again. |
| D13 | Check 1 sees the full masked instruction, including the function signature. That is exactly what an agent would see. |
| D14 | Check 1 fails on any clue span. The owner can override in the review sheet. |
| D15 | Instruction, reference code, and unit tests come from the benchmark **unchanged**. Masks are new; they are the method. |
| D16 | No World gaps. Skip extra gaps and Checks 2, 3, and 4. |

---

## 2. Rules for the agent running this plan

- **R1. Scope.** Do only the steps in Section 3. Do not start Stage 2 work. Do not add benchmarks, seeds, domains, checks, or features.
- **R2. Do not change these.** The decisions in Section 1, the seed draw rule, the success thresholds, and anything in `docs/`.
- **R3. Do not delete.** Delete nothing outside `pilot/runs/pilot_v0/`, with one exception: code in `pilot/scripts/` that this plan replaces. Leave `pilot/runs/selftest/` and `pilot/runs/mixed_offline/` as they are; they are historical. Do not commit or push.
- **R4. Where to write.**
  - Code: you may edit the files in `pilot/scripts/` and add new files there.
  - Outputs: write them to `pilot/runs/pilot_v0/`.
  - Dependencies: add packages with `uv add`.
  - **Read, never write:** `docs/current/`. Use `docs/archive/` only to look up background; never act on it.
- **R5. When this plan does not cover a case:**
  1. Do not invent a rule.
  2. Write the case to `pilot/runs/pilot_v0/QUESTIONS.md`: what happened, the options you see, and what you did meanwhile.
  3. Mark the affected seed or gap as `needs_review`, then continue with the others.
  4. Stop the whole run only if the case affects every seed.
- **R6. Log departures.** Write every place you had to depart from this plan as one dated line in `pilot/runs/pilot_v0/DEPARTURES.md`. Create the file even if it stays empty.
- **R7. Budget.** At most 100 model calls in total. Stop at 60 minutes of wall-clock time for the live run (Step 7). If either limit is reached, stop and still write `summary.json` and `review.md` from what is finished.
- **R8. No retries for bad builder output.** If a span does not match the instruction exactly, reject the gap and record the reason. Only network or API errors are retried.

---

## 3. Steps

Each step has a **Done when** line. Do not start a step until the step before it is done.

### Step 1. Switch the model client to OpenAI

- Rewrite `pilot/scripts/llm.py` to use the official `openai` Python SDK with structured JSON-schema output. Keep the same public function: `call_json(system, user, schema, cache_dir, tag) -> (parsed, record)`.
- Read the model name from the environment variable `PILOT_MODEL`, and the key from `OPENAI_API_KEY`. Neither has a default; fail with a clear message if either is missing.
- Keep the current behavior:
  - cache each call by content hash in `<run>/llm/`, storing the raw request and response;
  - retry only on rate-limit, server, and connection errors;
  - put a hard time limit on each call;
  - raise `LLMError` with a failure class (`refusal`, `truncated`, `api_error`, `timeout`, `model_mismatch`).
- Record in each cache file: the requested model, the served model, every request parameter, the token usage, and the latency. Raise `model_mismatch` if the served model does not start with the requested name.
- Do not set `temperature` or `seed` unless the model accepts them. Record whatever was sent.
- Count model calls across the run, and stop at the R7 limit.

**Done when:** a unit test with a mocked client passes, and `import llm` works without a key.

### Step 2. Draw the 20 seeds

1. Start from all 1,140 task IDs in `data/raw/bigcodebench/v0.1.4.jsonl`. Do not filter them.
2. Sort the IDs by task number. Shuffle with `random.Random(20261029)`. Take the first 20.
3. Write `pilot/runs/pilot_v0/seeds.jsonl` in the same format as `pilot/seeds.jsonl`, without the `gold_check` and `why_picked` fields. Write `pilot/runs/pilot_v0/seed_draw.json` with the RNG seed and the full shuffled order.

Do not run any task code. Do not use `pilot/candidates_prefilter.json` or `pilot/scripts/mine_candidates.py`; they are the old filter. Do not swap, add, or remove seeds by hand, even if one looks poor. A poor seed is a result.

**Done when:** `seeds.jsonl` has exactly 20 seeds, and `seed_draw.json` exists.

### Step 3. Update the prompts and schema

- **Prompt source:** change `prompts.py` so it reads all prompt text from `docs/current/prompts_v0.md`. That file has two `text` blocks, found by their headings:
  - `## Builder`: the v0 builder prompt. Its only inputs are `{{task_id}}`, `{{full_instruction}}`, and `{{gold_solution}}`.
  - `## Check 1`: the PB Prompt 1D prompt, verbatim.
- **Remove** `PILOT_BUILDER_ADDENDUM`.
- **No prompt text in code:** do not copy or retype prompt text into Python.
- **Rewrite `BUILDER_SCHEMA`** to match the JSON in the builder prompt exactly:
  - fields: `status`, `skip_reason`, and `candidate_subparts`;
  - each subpart has `subpart_id`, `variable`, `original_value`, `alternative_values`, `spans_removed`, and `replaced_with`;
  - if the API's schema mode accepts `minItems`/`maxItems`, make `alternative_values` require exactly one item. If it does not, gate G2 checks it.

**Done when:** `prompts.py` loads, and the schema validates the fixtures in Step 6.

### Step 4. Update the gatekeeper and the build script

For each seed and gap, the pipeline runs these checks in this order. The first failure ends the checks for that seed or gap.

| # | Check | If it fails |
|---|---|---|
| G1 | The builder returned `ok`. | Seed `skipped_by_builder`, with the builder's reason |
| G2 | The gap has exactly one alternative value, and `spans_removed` and `replaced_with` have the same length. | Gap `rejected: malformed` |
| G3 | Every span occurs word for word in the full instruction, and the masking splice succeeds. | Gap `rejected: splice` |
| G4 | Check 1 (Step 5) passes. | Gap `rejected: leakage` |

Then:
- A gap that passes G2–G4 is `accepted`.
- Keep `surface_flags` (it warns the reviewer and does not change the verdict).
- **Remove** from the pipeline path:
  - the reference check on each seed (the `run_suite` call on the gold solution in `process_seed`);
  - the test run on gaps (`gatekeeper.test_run`);
  - the `test_mutation` and gold-mutation code;
  - the multi-gap entries;
  - the distractor handling;
  - the multi-gap Check 1.
- In `build_dataset.py` and `make_review.py`, write the outputs in Step 8 and the schema in `stage1_method_v0.md`, Step 5. `rejected.jsonl` replaces `candidates.jsonl`.

**Done when:** the unit tests in Step 6 pass.

### Step 5. Check 1

- Run the Check 1 prompt from `prompts_v0.md` on each gap that passed G2–G3.
- **The reader's input** is the full single-gap masked instruction, including the function signature (D13).
- **Option order:** put the original value and the one alternative value in an order shuffled with `random.Random(f"{seed_id}:{subpart_id}")`. Store the order.
- **Pass:** `leftover_clue_spans` is empty. If the reader also picked option 1 or 2, record `note: "prior_lean"`.
- **Fail:** any clue span is listed. Record each span, and whether it appears verbatim in the masked text.

**Done when:** Check 1 results are stored in the audit file of each gap.

### Step 6. Offline tests (no model calls)

Update `pilot/scripts/test_pipeline.py` so that all of these pass with `uv run python -m unittest` from `pilot/scripts`. Remove the tests for code that Step 4 removed.

1. **Splice:** exact replacement; a span that is not found is rejected; text that was not targeted is unchanged; a span that occurs twice is replaced in both places and flagged.
2. **Gates:** one case each for G1 (builder skip), G2 (two alternative values), G3 (span not found), and an accepted gap.
3. **Check 1 mapping:** with a fake reader response, the choice maps back to `original_value` / `alternative_value` correctly for both option orders, and `prior_lean` is set when expected.
4. **Real-seed fixture 985 (expected `accepted`, with Check 1 skipped):**
   - Spans: `["round it down to the nearest integer"]` → `["convert it to an integer"]`.
   - Original value `round down`, alternative `round to the nearest integer`.
5. **Offline end-to-end:** run `build_dataset.py --builder-json <fixtures> --no-check1` on seed 985. Make sure the outputs in Step 8 are written and the counts are correct.

Fixture 4 is for testing only. It is not a dataset entry.

**Done when:** all tests pass. Write the test output to `pilot/runs/pilot_v0/offline_tests.txt`.

### Step 7. Live run

```bash
uv run python pilot/scripts/build_dataset.py --seeds pilot/runs/pilot_v0/seeds.jsonl --run-dir pilot/runs/pilot_v0
```

- Run it once. The model-call cache makes a re-run after a crash free for calls that already finished.
- Run the 20 seeds in parallel, as now.
- Record the wall-clock time of each stage per seed: builder, splice, Check 1.

**Done when:** every seed has a final status, or the R7 limit was reached.

### Step 8. Write the outputs

Write these to `pilot/runs/pilot_v0/`:

| File | Content |
|---|---|
| `dataset.jsonl` | Accepted gaps only, one line each, schema in `stage1_method_v0.md`, Step 5. |
| `rejected.jsonl` | Every gap that was not accepted, with the gate that stopped it and the reason. Also one line per seed that the builder skipped or that errored. |
| `audit/<seed>.json` | Everything for one seed: builder output, each gate's evidence, Check 1 option order and result, timings. |
| `llm/` | Raw request and response of every model call. |
| `summary.json` | The counts and timings in Section 5. |
| `review.md` | The review sheet in Section 6. |
| `QUESTIONS.md` | Only if R5 was used. |
| `DEPARTURES.md` | Every departure from this plan (R6). Can be empty. |

**Done when:** all files exist, and the numbers in `summary.json` match the line counts of `dataset.jsonl` and `rejected.jsonl`.

### Step 9. Report

End with a short message to the owner that contains:
- the `summary.json` numbers;
- the success check (Section 5), one line per criterion: met, not met, or "owner to judge";
- the path to `review.md`;
- every entry in `QUESTIONS.md`, and every line in `DEPARTURES.md`.

---

## 4. Dataset entry schema

Use the schema in `stage1_method_v0.md`, Step 5, exactly. It keeps S1's structure (`reference_ambiguities` is a list, here with one item) so that the Stage 2 prompts still work.

---

## 5. Summary and success check

### `summary.json` contents

- **Seeds:** drawn, builder `ok`, builder `skip_seed_task`, builder error.
- **Gaps:**
  - proposed;
  - stopped at each gate (G2, G3, G4, one count each);
  - accepted.
- **Seeds with at least one accepted gap.**
- **Check 1:** pass, `prior_lean`, fail.
- **Model calls:** count; tokens in and out; served model name(s).
- **Wall-clock time:** total, plus median and maximum per seed for each stage.
- **Questions:** the number of entries in `QUESTIONS.md`.

### Success criteria

These are the owner's four goals. The numbers are proposals; the owner can change them before the run.

| Goal | Criterion | Measured by |
|---|---|---|
| Enough usable gaps | At least 5 of 20 seeds have one or more accepted gaps. The share of seeds the builder skips is reported as a finding, with no threshold. | `summary.json` |
| Gaps look right | The owner marks at least 80% of accepted gaps `keep`, and agrees with at least 80% of the builder's skip decisions, in the review sheet. | Owner, after the run |
| Fast and unattended | Step 7 finishes in under 30 minutes with no input from the owner, and `QUESTIONS.md` has 2 or fewer entries. | `summary.json`, `QUESTIONS.md` |
| Full audit trail | For every proposed gap, `audit/` shows the gate that decided it and the evidence. Every model call has a file in `llm/`. | Spot check by the owner |

---

## 6. Review sheet (`review.md`)

**At the top:**
- the `summary.json` numbers in a table;
- a reading guide: one sentence per field.

**One section per seed:**
- seed status and the builder's skip reason, if any;
- **for each accepted gap:**
  - a word diff of the full vs. masked instruction;
  - original value vs. alternative value;
  - the Check 1 result: the reader's choice mapped back to the values, confidence, and clue spans;
  - two blank lines for the owner:

    ```text
    Owner verdict (keep / drop):
    Reason:
    ```

  - a check list for the owner:
    - Is the removed detail a setting, not the goal of the task?
    - Is the alternative realistic?
    - Does the reference code really do what the instruction says for this detail?
    - Would the two values lead to visibly different code or output?
    - Does the masked text still read naturally?
    - Is there a clue the reader missed?
- **for each seed the builder skipped:** the full instruction, the builder's skip reason, and one blank line for the owner: `Agree with skip (yes / no):`.
- **for each gap that was not accepted:** one line with the gate that stopped it and the reason. Put `leakage` rejections first, with the clue spans and an override line for the owner.

# Stage 1 pilot — decision log

Every choice made while building the pilot, and every place it departs from
`stage1_dataset_construction_methodology.md` / `dataset_selection_and_fast_construction_guide.md`
(abbreviated **S1** and **CG**). Newest entries at the bottom of each section.

## Scope (agreed with user)

| Decision | Value | Source |
|---|---|---|
| What is built | Stage 1 pipeline end to end: adapter → builder LLM → Python gatekeeper → Check 1 | user choice |
| Seed source | BigCodeBench v0.1.4 (`instruct_prompt` split) | user choice |
| Models | Claude only; builder + Check 1 reader = `claude-opus-5-5` | user choice |
| Pilot size | 5 seed tasks | user choice |
| Env | uv project (`pyproject.toml`), Python 3.12 | user instruction |

## Environment

1. **pandas pinned to 2.2.3, numpy < 2.** With pandas 3.0, the *gold* solution of BigCodeBench/889
   fails 3 of its own 6 tests (copy-on-write makes `df[col].fillna(..., inplace=True)` a no-op; new
   string dtype breaks `np.issubdtype`). The test-run cruciality check (S1 Step 3B) is meaningless if
   gold fails, so the env must match the benchmark's era. **Implication for Stage 2:** the agent's
   sandbox must use the same pins, or agents get blamed for environment drift.
2. Raw parquet converted once to `data/raw/bigcodebench/v0.1.4.jsonl`.

## Seed selection (CG Layer 1 — deterministic, 0 LLM calls)

3. `pilot/scripts/mine_candidates.py`: keep tasks whose libs ⊆ a light set (stdlib + pandas/numpy/pytz)
   and whose `instruct_prompt` matches ≥2 allowlist regexes (CG 4.3). 49 / 1140 pass.
4. From those 49, 5 picked **by hand** to cover different allowlist types (missing-value policy,
   duplicate policy, tie-break, rounding, sort order). Hand-picking is a selection-bias risk for a
   paper; for the full dataset, replace with a documented rule or random draw from the prefiltered pool.
5. Each seed's gold solution passes 100% of its own tests in this env (`gold_check` in `seeds.jsonl`).
6. **Problem found by reading tests:** BigCodeBench/96's only allowlist parameter ("sorted by count
   descending") is never asserted (tests use `assertIn` / set membership). It cannot be Crucial under
   S1 Step 3B, so the seed likely fails S1 Step 1 Rule 4. The keyword prefilter cannot detect this; the
   gatekeeper's test-run should. (Awaiting user decision: keep as a negative control or swap.)
7. Pre-read of the other four (to be confirmed by the gatekeeper, not assumed):
   - 889 mean-fill: tested (`27.5`). Note **median is a bad alternative value**: every test column has 2
     non-NaN values, so mean == median and the swap would not flip any test.
   - 232 duplicates (keep-first → total 1200; keep-last → 900) and alphabetical tie-break: both tested.
   - 985 floor rounding (`1234567.89 → 1234567`; round-nearest gives `…568`) and "no extra index
     column" (`assert_frame_equal` vs. `read_csv`): both tested.
   - 526 key sorting (test_case_5 inserts `a, c, b`) and ignore-missing (`b: None → NaN`): both tested.

12. **User decision:** keep BigCodeBench/96 as a **negative control**. Expected outcome: the gatekeeper
    marks its sort-order subpart Non-Crucial and the seed ends `rejected_no_crucial`.
13. **Spec/gold mismatch in BigCodeBench/232:** the instruction says ties go to "the first category in
    alphabetical order", but gold uses `Counter.most_common(1)` (first-*seen*, not alphabetical), and the
    only tie test has `Electronics` both first-seen and alphabetically first. The stated rule is neither
    implemented nor tested. If the builder picks it, the test run should mark it Non-Crucial.

## Pipeline (CG 4.2 three-layer design) — `pilot/scripts/`

14. **Prompts are extracted verbatim from the docs at runtime** (`prompts.py`): builder = CG §4.4,
    Check 1 = playbook Prompt 1D. Anything added is in a separate `PILOT_BUILDER_ADDENDUM` constant.
15. **Builder addendum (departure from CG 4.4):** (a) signature default args count as spans;
    (b) `find_in_gold` must be unique; (c) new fields `target_tests` and `test_mutation` (edit to the
    unit tests so they expect `alternative_value`). (c) is needed to implement CG 4.2 Layer 3's
    "mutated gold … passes the mutated target assertion", which the CG 4.4 schema has no field for.
16. **Crucial is decided by the test run, not the builder** (S1 3B "Test Run preferred"). Rules in
    `gatekeeper.test_run`:
    - mutated gold fails ≥1 original test, AND every failing test is in `target_tests`
      (unmasked assertions still pass), AND mutated gold passes the mutated tests, AND original gold
      fails the mutated tests → `accepted`, `is_crucial: true`.
    - no test flips → `accepted`, `is_crucial: false` (usable as a distractor), even if the builder said
      Crucial; the override is recorded.
    - mutation breaks tests outside `target_tests` / crashes / no-op / non-unique anchor → `rejected`.
    - flip verified but the test mutation is unusable → `needs_review` (kept out of the dataset).
17. **Check 1 runs on the single-gap masked text of every surviving subpart** (crucial and distractor).
    Option order is shuffled with a seeded RNG (`seed_id:subpart_id`) and stored. Pass iff
    `leftover_clue_spans == []` (playbook rule). **No automatic re-masking on a fail** (CG 4.5 allows
    one): the subpart is rejected and shown for human override, so the pilot exposes how often it
    happens. The script also checks whether each cited clue appears verbatim in the masked text.
18. Check 1 is **not** re-run on the multi-gap version (masking more spans only removes text). Risk:
    two cuts could combine into a new artefact; the review sheet shows the multi-gap text.
19. **Single-gap versions: one per accepted Crucial subpart**, with `primary_for_category: true` on the
    first per category. S1 Step 4 says "one run for each category"; the extra versions let Stage 2
    choose. **Multi-gap main version** = all accepted Crucial + ≤1 accepted distractor, if ≥2 total.
20. **Skipped for this pilot:** Step 5 extra gaps (`extra_gaps: []`), W-Absent survival check
    (no World gaps in BigCodeBench), Checks 2–4.
21. **Sampling:** `claude-opus-5-5` does not accept `temperature`/`seed` (400). Stage 2 §3 "fix the
    temperature (and seed)" cannot be done as written for current Claude models; record the served
    model id and keep raw responses instead. Effort is fixed explicitly at `high` for builder and
    Check 1 (Opus 5.5's default would be `medium`).
22. **No server-side refusal fallback.** The skill's default for Opus 5.5 is `fallbacks: "default"`,
    but a fallback silently swaps the builder model mid-dataset. Instead every response's model is
    asserted, and refusals are logged as a failure class in `errors.jsonl`.
23. Every LLM call is cached by content hash under `<run>/llm/` (raw request + response), so re-runs
    resume, and the dataset is traceable to the exact responses. Cost = usage × $4/$20 per MTok.
24. **Gatekeeper self-test (offline, 0 LLM calls)**: `scripts/fixtures/make_selftest.py` feeds six
    hand-written subparts with known answers for seed 232 (1 correct, 4 broken, 1 distractor).
    All six got the expected verdict (`runs/selftest/review.md`).

## Known limitations of BigCodeBench as a seed source (flag for the paper)

8. **S1 Step 1 Rule 1 (multi-step / tool use) is weak**: each task is one function. It only becomes
   multi-step once wrapped in the Stage 2 harness (agent can run code / tests).
9. **No World gaps**: there is no persistent environment, so nearly every subpart will be Category
   `Task`, Answer Source `User`. S1 Rule 4 (World/User/Task mix) must come from other seed sources.
10. The `instruct_prompt` ends with the function signature, whose **default arguments can state a
    masked value** (e.g. `from_encoding='cp1251'` in task 728). The builder must list signature spans
    in `spans_removed`, and Check 1 must see the signature. Same issue as CG conflict #3 (tool schema leak).
11. BigCodeBench docstrings contain errors (e.g. BigCodeBench/0 says "Default is numbers from 1 to 10"
    but the signature default is `range(1, 3)`). Contradictory spans can look like leaks or clues.

## Benchmark-only correction — 2026-10-29

The user requires externally sourced benchmark seeds and requested deletion of assistant-authored examples. Both invented non-coding seeds, their generators, audits, masks, oracle/world bundles, pending-reader requests, and exported data were removed from the active workspace. The original two BigCodeBench examples remain. Test fixtures for software regression checks are infrastructure, not dataset entries.

Replacement sources must be researched before download. Preserve original task text, source-provided reference outcomes and graders, exact revisions, and checksums. Do not invent a replacement prompt, expected answer, or grader. Imported sources remain separate from constructed/verified candidates until audited. The offline/no-model preference remains in force.

The current run has two selected gaps and two pending candidate variants. The old `mixed_offline` directory name is retained for compatibility. Previously saved Site/Git versions may retain historical snapshots; this correction updates the current source and live publication without rewriting remote history.

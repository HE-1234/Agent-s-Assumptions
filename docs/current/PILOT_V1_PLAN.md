# Pilot v1 plan

Status: **in force.** Drafted by Codex in `pilot/runs/pilot_v1/proposed/`, adopted by the owner on 2026-10-31. Phase 1 (including the six-seed live dry run) is complete. Phase 2 still requires the exact owner instruction “Go ahead with Phase 2” and the owner naming the final Check 1 reader. No docs are edited by the runner. Stage 3 taxonomy is never a builder input.

## Inputs and sampling

- BigCodeBench v0.1.4: all 1,140 tasks, sorted by numeric task ID; shuffle with random.Random(20261030), take 60.
- WorkBench revision 49c7dfd00c03d384ec59ea57374f50b766aa5613: owner selected top_level for the dry run and for Phase 2. Exclude empty outcomes. For Phase 2 also exclude the union of rows whose parsed outcome differs from top_level in either dated snapshot; report exact file/row IDs. Concatenate domain files in filename order, preserving CSV row order; shuffle once with random.Random(20261030), scan in that order until 30 seeds, skipping a row if its domain already has six. Keep the full eligible/shuffled order and all exclusions.
- Gaia2 execution/validation: pinned revision in data/raw/gaia2/source_index.json. Preserve Parquet row order; exclude instructions inviting clarification, keeping exact evidence and scenario IDs. Shuffle with random.Random(20261030), take 30. Filter puzzles remain in the draw for the builder to skip; never replace skips.
- Dry run: owner authorized real model calls on two seeds per source, fewer than 30 calls (maximum 29). Use the first two of each source's corresponding dry-run shuffle; preserve every input packet. WorkBench disputed-outcome exclusions apply only to Phase 2, as instructed. No dry-run result enters the full build automatically.

## Steps and gates

1. Verify source hashes, parse stored files as data, prepare exact per-source builder packets listed in docs/current/prompts_v1.md. Never import or execute benchmark code. Retain record/function locations and complete records supplied. Missing or ambiguous evidence becomes a question; no silent truncation or invented lookup result.
2. Fresh GPT-6.1 Sol/high builder subagent per seed, at most three gaps or a reasoned skip. Preserve the exact request, raw response, requested model/effort, timing and schema. For large v1 inputs, a fresh agent may read only its designated immutable prompt packet; it receives no inherited chat or other context. No benchmark code execution is permitted.
3. G1: record builder skip. Validate output schema; uncovered invalid/contradictory output goes to QUESTIONS.md and needs_review, without repair or a content retry. A builder-reported false Test B is rejected; there is no independent semantic verifier.
4. G2: exactly one alternative and paired spans. G3: exact Python deletion; nonempty replacements are preserved only as the builder's claimed grammar repairs and explicitly shown for owner review. No new automatic semantic rule judges repairs. Missing exact spans reject the gap. Keep flags and every untouched character.
5. G4: unchanged Check 1 prompt; shuffle original/alternative with random.Random(f"{seed_id}:{subpart_id}"). Give the reader only the masked instruction and options. Any clue rejects; a choice without clues passes with prior_lean. Record verbatim presence of every clue.
6. Save accepted single-gap-delete entries using Section 8, plus rejected records, complete audits, model-call records, per-source summary, and review. Any undefined case is needs_review and a QUESTIONS.md entry; continue unaffected work.

## Models and budgets

Builder: the authorized fresh Sol/high subagent route, with transport limitations in DEPARTURES.md. Dry-run Check 1: Claude Opus 5.5/high (claude-opus-5-5) via signed-in Claude Code with --system-prompt. Owner explicitly authorized omitting --bare; tools, hooks, skills, memory, MCP and instruction-file loading are disabled. The dry-run reader is not the Phase 2 reader decision. Disable tools and inherited sessions for Check 1. Never substitute a model or silently fall back. Owner-authorized transport decoding may remove one complete outer Markdown JSON fence; preserve raw responses and all JSON values.

Phase 2: at most 400 model invocations and 4 hours, counted before dispatch with a shared budget. Stop dispatching at either bound and write partial reports. Raw requests/responses are cached within the run; never reuse an earlier run's cache. Unknown token usage/provider identity stays null. No benchmark task execution, commits, pushes, or deletion outside authorized folders.

## Outputs and success reporting

Full build: pilot/runs/pilot_v1/{dataset.jsonl,rejected.jsonl,audit/,llm/,summary.json,review.md,QUESTIONS.md,DEPARTURES.md}; draw/source-input manifests accompany them. Dry-run equivalents live only under dry_run/. Each review gap shows full/masked text, exact spans/repairs, original/alternative, Test B, dimension, answer source, observed original outcome, Check 1 evidence, and owner keep/drop lines.

Report per source: eligible/excluded/drawn seeds, skips, proposed gaps, rejections at each gate, accepted gaps and seeds, needs_review, model calls and elapsed time. Compare WorkBench all six version pairs, with three example diffs per changed domain. List Gaia2 invitation exclusions and WorkBench Phase 2 disputed-outcome exclusions.

Success: all specified offline checks and existing tests pass; counts reconcile to artifacts; every attempted seed/gap/call has evidence; source text and docs are unchanged; budget is respected. Owner judges content validity, grammar repair, alternatives and skips. No numeric yield or quality threshold has been supplied for v1; report observed values without inventing one.

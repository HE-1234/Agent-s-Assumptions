# Questions

## Q1 — Later model roles and masked-item restoration (2026-10-29)

What happened: the owner asked about a separate agent trying to restore the masked item and clarified that “6 luna” is the preference for a later separate agent acting as the user. These are distinct roles. Restoring a missing detail from the masked instruction corresponds to Check 1's blind reader; Check 2 instead reconstructs an instruction from extracted facts and is explicitly excluded from v0.

Options discussed: keep v0's fresh-context blind reader with shuffled original/alternative options and an undetermined choice; consider a later free-response restoration experiment, which would need owner-defined answer-matching rules; or consider a different reader model, which would change D2's one-model configuration. Configure “6 luna” for the later user simulator, not for the current builder or reader. Its API endpoint and exact model identifier remain to be established for that later phase; local API availability has not been verified.

Meanwhile: implemented the current Check 1 exactly and made no model calls. No extra agent, restoration experiment, or user simulator was run. The later configuration/experiment choices remain needs_review; no Phase 1 seed or gap is affected. No change to the current plan is inferred from this discussion.

Update (2026-10-29): the owner subsequently requested GPT-6.1 Sol/high Codex subagents for the live builder. Builder and fresh-context Check 1 subagents have now run; the execution-route departure is recorded in DEPARTURES.md. The later user simulator (“6 luna”) and optional restoration experiments remain unrun and outside v0. No dataset item is blocked by this discussion.

# Questions

## Q1 — Test output isolation (resolved, 2026-10-29)

What happened: the existing offline tests write temporary files and the 985 fixture to pilot/runs/pilot_v0/, which the owner requires to remain untouched. The existing subagent runner also hardcodes that baseline directory.

Options: run unchanged and violate baseline preservation, or redirect test writes and make the runner accept the explicitly requested run directory.

Meanwhile: selected output isolation as required by the owner; test assertions and prompts are unchanged, seed verification still reads the baseline, and all new test outputs go under pilot_v0_stakes/. No seed or gap is affected or requires a review decision.

# Instructions for coding agents

This is a research project. It builds a dataset of instructions with missing details, to study how AI agents handle assumptions.

- **Source of truth:** `docs/current/`. Read `docs/current/README.md` first, then the plan it names. Follow that plan exactly.
- **Background only:** `docs/archive/`. These are older plans. Never act on them. Where they disagree with `docs/current/`, `docs/current/` is correct.
- **Do not edit anything in `docs/`.** Only the owner changes plans and prompts.
- **When the plan does not cover a case,** do not invent a rule. Write the case to the run folder's `QUESTIONS.md` as the plan describes, then continue with the work that is not affected.
- **Environment:** a uv project with Python 3.12. Run pipeline code with `uv run`. The Stage 1 pilot runs no BigCodeBench task code; do not set up a task environment unless the current plan says so.

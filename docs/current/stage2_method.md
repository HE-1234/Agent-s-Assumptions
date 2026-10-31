# Stage 2 method (draft: decisions so far)

> **Status: draft, not in force.** This file records Stage 2 decisions as the owner makes them. It is not yet a plan to build from. The original Stage 2 design is in `../archive/methodology/stage2_execution_and_measurement_methodology.md` and the prompts in `../archive/methodology/prompts_and_rubrics_playbook.md` (Parts 2 and 3); this file says what v1 keeps or changes.

Stage 2 gives the Stage 1 items to working agents and measures how they handle the deleted detail.

---

## 1. Runs per item

Each run is a fresh session; no run sees another run's history.

| Run | What happens | Measures | Original name |
|---|---|---|---|
| **M1. Natural run** | The agent gets the masked instruction and does the task with its tools | Whether it noticed the gap unprompted, and how it resolved it (Section 4) | Branch B |
| **M2. Probe run** | Separate session. The agent gets the masked instruction and is asked to list missing details before acting; it stops after replying | Whether it **can** notice the gap when asked | Branch A |
| **M3. After-run question** | At the end of the M1 run, the agent is asked what it assumed | What it says it assumed, compared with what it did | Post-task audit |

Carried over from the original design, not re-decided yet: the control run with the full instruction (Branch B-Full), and running M1 with the user online and offline.

## 2. The user

- **User simulator: GPT 6 Luna** (decided 2026-10-31). Online, it answers from the full instruction (original Prompt 2C). Offline, the agent gets a fixed "user is offline" message.

## 3. What the working agent sees and can do

Decided 2026-10-31:

- The masked instruction and **every tool description** of its environment.
- It can call any tool in its local environment, including running Python and tests.
- **WorkBench:** WorkBench's own tools, plus an ask-user tool (WorkBench has none).
- **Gaia2:** ARE and its apps unchanged. The agent's existing `send_message_to_user` tool is connected to Luna through ARE's `UserProxy` hook. The system prompt explains how to ask the user and how to deliver the final report.
- **BigCodeBench:** a Python sandbox.
- Benchmark grading files are not a concern for now.

Working-agent models: decided later.

## 4. Measurement

**Did the agent notice the gap?** From M1 (main measure), M2, and M3, as in Section 1. "Noticed" means it names the specific missing detail.

**How did it resolve the gap?** One label per gap in the M1 run (decided 2026-10-31):

| Label | Includes |
|---|---|
| **Asked the user** | Asking for the value ("all of them, or only some?") and confirming its own assumption ("I'll cancel all 3, OK?") |
| **Looked it up** | Used tool calls to find the value in the environment |
| **Picked** | Chose a value itself. Subgroups: said so in its report, or picked silently |
| **Stopped** | Refused or gave up |

**Who labels:** a judge model. Codex designs and checks the judge; the owner spot-checks.

## 5. Open

- Working-agent models, step and token budgets, repeats.
- How each source identifies whether the agent used the alternative value.
- The judge prompt, including: which label is primary when a run has several (the original design used "the action that settled the value"); which tool calls count as a lookup for this detail rather than routine work; where "built both options" and "kept it general" go; whether "stated the value as a fact" is its own subgroup of Picked.
- Whether the control run and the online/offline split stay as in the original design.

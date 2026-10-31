# Stage 1: open questions

> **Archived on 2026-10-31.** Replaced by Stage 1 v1 in `docs/current/`. Do not act on this file.

> **Status (2026-10-29):** For pilot v0, the recommendation for each item below is in effect. `PILOT_V0_PLAN.md`, Section 1, records the decisions. If this document and the plan are different, the plan is correct. Keep this document as the explanation of each decision and as the glossary.
>
> **Superseded later the same day:** the owner decided not to use the unit tests to check gaps. Items A4, A5, A6, A8 and D3, Part 4 item 5 ("the test run stays, as a filter"), and all of Part 6 (the test-run procedure) no longer apply. Item C6 (seed filter) is also superseded: v0 draws 20 seeds at random from all BigCodeBench tasks, with no filter, and Stage 1 runs no task code. In Stage 2, a judge reads the agent's code and output to see which value it used. See `stage1_method_v0.md`.

**How to use this document**

- This document is written in the style of ASD-STE100 (Simplified Technical English). The sentences are short. Each sentence has one topic.
- I did not examine each word against the STE dictionary. Some technical words (for example, "benchmark" and "unit test") are technical names. Part 2 gives a definition for each of them.
- Part 5 has the questions. Each question has a line "**Your answer:**". Write your answer on that line.

---

## Part 1. What this project does

This project examines how an AI agent operates when an instruction does not give all the necessary information.

An AI agent is a language model that can use tools. For example, it can read files, run code, and send a message to the user.

When an instruction does not give a detail, the agent can do one of these:

- Ask the user.
- Look for the detail in its environment (for example, in files or in a database).
- Select a value itself. This document calls this an "assumption".
- Stop.

The project measures five things:

| Name | Question |
|---|---|
| RQ1 | Does the agent see that a detail is missing? When does it see this? |
| RQ2 | What does the agent do about the missing detail? |
| RQ3 | Which value does the agent select when it does not ask? |
| RQ4 | At the end, does the agent tell the user about its assumption? |
| RQ5 | When the agent gets new information during the task, does it change its earlier decisions? |

The project has two stages:

- **Stage 1** makes the dataset. The dataset contains instructions with missing details. For each instruction, the dataset also records the correct missing details.
- **Stage 2** gives these instructions to agents. Then it measures RQ1 to RQ5.

This document is about Stage 1 only.

---

## Part 2. Words used in this document

**Benchmark.** A published set of tasks that researchers use to test AI models. Examples: BigCodeBench, WorkBench, TravelPlanner.

**Seed task.** One task that we take from a benchmark. A seed task has three parts:

1. **Full instruction.** The text that tells the agent what to do. It gives all the details.
2. **Reference solution.** Correct work for the task. In a coding task, this is correct code. The documents also call it the "gold solution".
3. **Grader.** A program that tells if the work is correct. In a coding task, the grader is a set of unit tests.

**Unit test.** A small program that runs the code with one input. It compares the result with the expected result. The result of each unit test is "pass" or "fail".

**Gap.** One detail that we remove from the full instruction. Example: the full instruction says "replace the missing values with the mean of the column". The gap is "with the mean of the column".

**Masking.** The procedure that removes a gap from the full instruction. The result is the **masked instruction**.

**Span.** The exact words in the full instruction that state the gap. One gap can have more than one span, because an instruction can state the same detail in two places.

**Original value.** The value of the gap in the full instruction. Example: "mean".

**Alternative value.** A different value that is also realistic. Example: "median", or "remove the rows".

**Crucial gap.** A gap where the value changes the result of the grader. If the work uses the alternative value, the grader gives "fail".

**Non-Crucial gap (distractor).** A gap where the value does not change the result of the grader. Stage 2 uses distractors to find agents that ask too many unnecessary questions.

**Category label.** A label that tells what the gap is about. There are three labels:

- **World:** a fact about the environment (files, software, databases). Example: "The configuration file is in `/etc/app/`."
- **User:** a fact about the person. Example: "My budget is $200."
- **Task:** a rule about the work. Example: "Save the result as a CSV file."

**Answer source label.** A label that tells where the agent can find the missing detail:

- **User:** only the user knows it. The agent must ask.
- **World:** the agent can find it in the environment.
- **Both:** the agent can ask, or it can look.

**Single-gap version.** A masked instruction with one gap removed.

**Multi-gap version.** A masked instruction with 2 to 4 gaps removed at the same time.

**Builder.** The step where a language model reads the seed task and proposes gaps. For each gap, it gives the spans, the original value, the alternative value, and a change to the reference solution.

**Mutation.** The small change to the reference solution that makes it use the alternative value. The result is the **mutated solution**. Example: change `mean()` to `median()`.

**Test run.** The step that runs the unit tests on the mutated solution. It shows if the gap is Crucial. The documents record this as `crucial_evidence: "test_run"`.

**Gatekeeper.** The Python program that does the automatic checks on the builder output. It does the masking and the test run.

**Check 1 (leakage check).** A second language model reads only the masked instruction. It tries to guess the removed value. If other words in the masked instruction tell the value, the mask "leaks". We cannot use a gap that leaks, because the agent does not need to make an assumption.

**Blind reader.** The language model that does Check 1. It is "blind" because it does not see the full instruction.

**Clue span.** Words in the masked instruction that the blind reader uses as evidence for its guess.

**Prior lean.** The blind reader selects a value, but it gives no clue span. This means that the reader uses only its general knowledge. This is not a leak.

**User simulator.** In Stage 2, a language model that acts as the user. It answers the agent's questions with information from the full instruction.

**Stage 2 branches.** Stage 2 runs each task in different ways:

- **Branch A:** the agent reads the masked instruction and lists the missing details. It does not do the task.
- **Branch B:** the agent does the task with the masked instruction. The user is "online" (the user simulator answers) or "offline" (no answer).
- **Branch B-Full:** the agent does the task with the full instruction. This is the control.

**Short names for the documents:**

| Short name | File |
|---|---|
| S1 | `docs/archive/methodology/stage1_dataset_construction_methodology.md` |
| S2 | `docs/archive/methodology/stage2_execution_and_measurement_methodology.md` |
| PB | `docs/archive/methodology/prompts_and_rubrics_playbook.md` (the exact prompts) |
| CG | `docs/archive/methodology/dataset_selection_and_fast_construction_guide.md` (the "companion guide") |
| DL | `docs/archive/pilot_history/DECISIONS.md` (the decision log that the agents wrote) |
| LR | `lib/dataset_selection_review_2026-10-25.md` (the review of datasets) |

---

## Part 3. The Stage 1 procedure, as S1 describes it

1. Select seed tasks from a benchmark.
2. Find the gaps in each seed task.
3. Give three labels to each gap: category, Crucial or Non-Crucial, and answer source.
4. Remove the gaps to make the masked instructions.
5. (Optional) Find other missing details. These are details that the full instruction also does not give.
6. Do the quality checks. Check 1 is necessary. Checks 2, 3, and 4 are optional.
7. Save each item in the dataset file.

---

## Part 4. Decisions that you made

Version 0 (v0) is the first small version of the dataset. You decided to skip these items in v0:

1. **Multi-gap versions.** v0 has single-gap versions only.
2. **A search for distractors.** The builder does not look for Non-Crucial gaps.
3. **A second masking attempt after Check 1 fails.** If Check 1 fails, we reject the gap.
4. **The W-Absent check.** This check removes a World fact from the environment. Then it makes sure that the task still operates. v0 has no World gaps, so v0 does not need this check.
5. **Labels.** No Category (World, User, Task), no Answer Source, and no Crucial/Non-Crucial label. The test run stays, as a filter: a gap stays only if the unit tests detect it. See `stage1_method_v0.md`, Step 3.

---

## Part 5. Conflicts between the documents

Each item has four parts:

- **The documents say:** what each document tells you to do.
- **The problem:** why the difference is important.
- **My recommendation:** what I think we must do.
- **Your answer:** write your answer here.

### Group A. How Stage 1 finds and checks gaps

#### A1. Do we find all the details, or only the good gaps?

**The documents say:**

- S1 (Step 2) and PB (Prompts 1A, 1B, 1C): divide the full instruction into all its single facts. Give labels to each fact. Then select the facts to remove.
- CG (Section 4): do not do this. One language model call selects 3 Crucial gaps or fewer, and 1 distractor or fewer.

**The problem:** The S1 method needs many language model calls. One instruction can have 15 to 25 facts. Most of these facts are not usable gaps (for example, "use Python"). The CG method is faster. But two other parts of the documents need the full list of facts: Check 2, and the user simulator (PB Prompt 2C).

**My recommendation:** Use the CG method. Find only the good gaps. In v0, the user simulator can use the full instruction, because v0 has no World gaps.

**Your answer:**

#### A2. What removes the words: a language model or a program?

**The documents say:**

- S1 (Step 4) and PB (Prompt 1C): a language model removes the words. It can also correct the grammar.
- CG (Section 4.2): a Python program removes the exact words that the builder gives.

**The problem:** A language model can change other words by accident. A Python program cannot. But a Python program cannot correct the grammar.

**My recommendation:** Use the Python program. The builder gives a replacement text for each span. The replacement text includes the grammar correction. Example from BigCodeBench/985: "round it down to the nearest integer" becomes "convert it to an integer".

**Your answer:**

#### A3. How large can the change to the reference solution be?

**The documents say:** CG (Section 4.2) says that the mutation is one line.

**The problem:** Some gaps need a change of more than one line in the reference solution.

**My recommendation:** Permit any small change. The gatekeeper finds the location of the change with a text that occurs only one time in the reference solution.

**Your answer:**

#### A4. How do we prove that a gap is Crucial?

**The documents say:**

- S1 (Step 3B): make a solution for the alternative value. If this solution fails the original unit tests, the gap is Crucial.
- CG (Section 4.2, Layer 3): also, the mutated solution must pass a changed unit test that expects the alternative value. CG does not tell where this changed unit test comes from. In the first session, I told the builder to also write the changed unit tests (DL item 15).
- PB (Prompt 1B, Rule B): adds one more question to the same rule: "Can the agent still try the task?"

**The problem:** The builder must write correct test code for the changed unit tests. This is difficult. Most of the errors in the pilot came from this step.

**My recommendation:** Do not write changed unit tests. Part 6 explains the procedure that replaces them.

**Your answer:**

#### A5. Can a language model decide "Crucial" when we cannot do a test run?

**The documents say:**

- S1 (Step 3B): yes. Record it as `crucial_evidence: "llm_label"`.
- CG and DL: use the test run only.

**The problem:** The opinion of a language model is weaker evidence than the result of a test.

**My recommendation:** v0 uses the test run only. Thus v0 uses only seed tasks that have unit tests that we can run.

**Your answer:**

#### A6. What does "Non-Crucial" mean?

**The documents say:**

- S1 (Step 3B): Non-Crucial means "safe to ignore". In Stage 2, if the agent asks about a Non-Crucial gap, this counts as an unnecessary question. This decreases the precision score of the agent.
- DL (item 16): if no unit test changes from "pass" to "fail", the gap is Non-Crucial.

**The problem:** Sometimes no unit test fails because the unit tests are weak. It does not always mean that the detail is unimportant. Two examples:

- BigCodeBench/96 says "sort by count, largest first". No unit test examines the order. But the order is important to a real user.
- BigCodeBench/889 with "median" in place of "mean". Each test column has only two numbers. With two numbers, the mean and the median are the same.

If we label these gaps Non-Crucial, an agent that asks a good question gets a lower score.

**My recommendation:** Use a third label: "untested". Do not put "untested" gaps in v0.

**Your answer:**

#### A7. How many alternative values does each gap have?

**The documents say:**

- S1 (Step 2): one or more.
- CG (Section 4.4): a list.
- PB (Prompt 1A): one.
- Check 1 (PB Prompt 1D): it compares exactly two values (the original value and one alternative value).

**The problem:** If a gap has two or more alternative values, the documents do not tell which one goes to Check 1 and to the mutation.

**My recommendation:** Exactly one alternative value for each gap in v0.

**Your answer:**

#### A8. How many single-gap versions does each seed task get?

**The documents say:**

- S1 (Step 4): one for each category that the task has.
- DL (item 19): one for each Crucial gap.

**The problem:** You decided not to use category labels now. Thus the S1 rule does not operate.

**My recommendation:** One single-gap version for each Crucial gap.

**Your answer:**

### Group B. Check 1 (the leakage check)

#### B1. What text does the blind reader see?

**The documents say:**

- PB (Prompt 1D): the masked instruction only.
- CG (Section 3 and Section 4.5): the masked instruction and the tool descriptions.

**The problem:** In BigCodeBench, the instruction ends with the first line of the function. Example: `def task_func(json_data, output_dir=".", file_name="country_population_report.csv"):`. The default values in this line can tell the removed value. In Stage 2, the tool descriptions can also tell the removed value.

**My recommendation:** The blind reader sees all the text that the agent sees at the start of Branch B.

**Your answer:**

#### B2. Does each clue span cause a "fail", or only a real clue?

**The documents say:**

- PB (Prompt 1D): the gap fails only if the clue is real. A person can change a "fail" to a "pass", and must write the reason.
- The current program: the gap fails if the blind reader gives any clue span.

**The problem:** The blind reader sometimes gives a clue span that is not a real clue.

**My recommendation:** The program fails the gap if there is any clue span. You examine each failure in the review sheet. You can change a "fail" to a "pass", and you write the reason.

**Your answer:**

#### B3. Can Stage 1 use a language model at all?

**The documents say:**

- S1 (Step 6): Check 1 is necessary. Check 1 is a language model call.
- CG (Section 4.2): the builder is a language model call.
- DL (entry of 2026-10-29, written by Codex): "The offline/no-model preference remains in force."

**The problem:** Because of the DL rule, Codex wrote the builder output by hand (file `pilot/runs/mixed_offline/builder_fixtures.json`). Check 1 did not run. The result: 0 items are complete. If no language model call is permitted, no gap can pass Check 1. Then the dataset stays empty.

**My recommendation:** Permit language model calls for the builder and for Check 1 only. Another possibility: a person does the blind reading. I do not know the reason for the offline rule. Please tell me the reason.

**Your answer:**

### Group C. Sources and rules

#### C1. Which benchmark do we use?

**The documents say:**

- CG (Section 2.2): BigCodeBench is the fastest.
- S2 (Section 1): SWE-bench, Terminal-Bench, and DAEval.
- LR: Terminal-Bench, Agent-Diff, and TravelPlanner.
- The pilot: BigCodeBench.
- Codex downloaded WorkBench and TravelPlanner (folder `data/raw/`). These are not yet in the pipeline.

**The problem:** The agents select different benchmarks in different sessions.

**My recommendation:** Use BigCodeBench for v0, because it already operates in the pipeline. Add other benchmarks after v0 operates through Stage 2.

**Your answer:**

#### C2. BigCodeBench does not obey S1 Rule 1.

**The documents say:** S1 (Step 1, Rule 1): the task must have many steps. The agent must make decisions or use tools.

**The problem:** Each BigCodeBench task is one Python function. A reviewer can say that the tasks are too simple for a study of agents.

**My recommendation:** Accept this for v0. In Stage 2, the agent can still run code and tests, so the task has more steps. Write this limit in the paper.

**Your answer:**

#### C3. Do we use all three domains now?

**The documents say:**

- S2 (Section 1) and CG: 50% coding, 25% workspace (calendar, email), 25% planning (travel).
- LR: these numbers are only a proposal.
- The pilot: coding only.

**The problem:** Each new benchmark needs a new adapter. An adapter is a program that changes the format of the benchmark to our format. This is the slowest work in Stage 1.

**My recommendation:** v0 uses coding only. Run v0 through Stage 2. Then add the other domains.

**Your answer:**

#### C4. Can we write text that is not in the benchmark?

**The documents say:**

- DL (entry of 2026-10-29): use only published tasks. Do not write new instructions, answers, or graders.
- S1 (Step 1): seed tasks can come from "an existing benchmark or curated task bank".
- CG (Section 3): rewrite each τ²-bench conversation into one new instruction.

**The problem:** The method itself makes new text: the masked instruction and the mutation. Also, Codex wrote the masks and mutations in `builder_fixtures.json` by hand. If the rule "write nothing" also applies to masks and mutations, we cannot make the dataset.

**My recommendation:** The full instruction, the reference solution, and the unit tests must come from the benchmark without change. The masks and the mutations are new. They are the method, and the checks examine them.

**Your answer:**

#### C5. Which language models do we use in Stage 1?

**The documents say:**

- DL (Scope): Claude only (`claude-opus-5-5`) for the builder and Check 1.
- S1 (Check 3): three models from three different companies.
- S2: Claude is also one of the agents that we test.

**The problem:** If the same model family makes the dataset and also takes the test, a reviewer can say that the test is not fair (for Claude or against Claude).

**My recommendation:** Claude only for v0. Write this limit in the paper. Add other models in a later version.

**Your answer:**

#### C6. How do we select the seed tasks?

**The documents say:** DL (item 4): I selected the 5 pilot tasks by hand.

**The problem:** Selection by hand can cause bias. A reviewer can say that we selected the tasks that give the result that we want.

**My recommendation:** Write a filter rule. Apply the rule to all tasks in the benchmark. Then select a random sample from the tasks that pass the rule.

**Your answer:**

### Group D. The connection to Stage 2

#### D1. Stage 2 needs a "main version" of each task.

**The documents say:** S2 (Section 4, Run Budget): the main version is the multi-gap version.

**The problem:** You decided to skip multi-gap versions. Thus each single-gap version needs its own Stage 2 runs: Branch A, Branch B with the user online, and Branch B with the user offline. A seed task also needs one Branch B-Full run. A seed task with 3 gaps then needs 1 + (3 × 3) = 10 runs, not 4.

**My recommendation:** Accept this. Before Stage 2 starts, count the runs and calculate the cost.

**Your answer:**

#### D2. We cannot fix the temperature.

**The documents say:** S2 (Section 3): fix the temperature and the seed of each model. Temperature is a setting that controls how random the output of the model is. Seed is a number that makes random output repeatable.

**The problem:** `claude-opus-5-5` does not accept these two settings (DL item 21).

**My recommendation:** Record the exact model name of each call. Keep all the responses. Use the repeats that S2 already tells you to do (k = 3) to measure how stable the agent's choices are.

**Your answer:**

#### D3. How does Stage 2 know which value the agent used?

**The documents say:**

- S2 (RQ3): for each gap, find if the agent used the original value, the alternative value, or a different value.
- CG (Section 3, Conflict 5): Stage 1 must make a program that finds this.
- S1 (Step 7): the dataset format has no field for this program.

**The problem:** Without this program, Stage 2 cannot measure RQ3.

**My recommendation:** The procedure in Part 6 also gives this. Add its output to the dataset format.

**Your answer:**

#### D4. Do we do the optional steps?

**The documents say:** S1 has one optional step and three optional checks:

- **Step 5 (find other missing details).** A language model reads the masked instruction and lists all the missing details. Some of these details are also missing from the full instruction. Then Stage 2 does not count questions about these details as unnecessary.
- **Check 2 (completeness).** A language model rebuilds the instruction from the list of facts. This makes sure that the list of facts is complete. It is necessary only with the S1 method in A1.
- **Check 3 (three-model votes).** Three models from different companies give the category and answer source labels.
- **Check 4 (human check).** A person examines 50 to 100 dataset items.

**The problem:** You did not decide about these yet.

**My recommendation:** Skip Step 5, Check 2, and Check 3 in v0. Do Check 4 before you publish.

**Your answer:**

#### D5. LR proposes changes to Stage 2 that are not in S2 or PB.

**The documents say:** LR (Section 8) proposes these changes:

- Separate the outcome, the interpretation, and the belief (8.1).
- Examine each channel of information (8.2).
- Separate questions that ask for information from questions that ask for permission (8.3).
- Complete the factorial control of the runs (8.4).
- Correct the categories that tell how the agent reports its assumptions (8.5).
- Do not make false psychological or statistical conclusions (8.6).

**The problem:** S2 and PB do not include these changes. An agent that reads LR and S2 gets different instructions.

**My recommendation:** These changes do not stop Stage 1. Decide about them before Stage 2.

**Your answer:**

---

## Part 6. The proposed change to the test procedure (A4 and D3)

### 6.1 The current procedure

For each gap, the builder writes three things:

1. The spans to remove.
2. The mutation (the change to the reference solution).
3. Changes to the unit tests. The changed unit tests expect the alternative value.

Then the gatekeeper examines four conditions:

- **(a)** The mutated solution fails the original unit tests that examine the gap.
- **(b)** The mutated solution passes all the other original unit tests.
- **(c)** The mutated solution passes the changed unit tests.
- **(d)** The original reference solution fails the changed unit tests.

Item 3 (the changed unit tests) has two purposes:

- Conditions (c) and (d) show that the mutated solution is a correct solution for the alternative value.
- In Stage 2, the changed unit tests can show if the agent used the alternative value.

**The problem:** Item 3 is the most difficult output for the builder, because the builder must write correct test code. Most of the errors in the pilot came from this item.

### 6.2 The proposed procedure

The builder writes only items 1 and 2. It does not write changed unit tests.

In Stage 1, the gatekeeper does these steps:

1. Run the original unit tests on the mutated solution.
2. Make sure that conditions (a) and (b) are true. These conditions are the same as before.
3. Make sure that each failed unit test shows a wrong value. If the mutated solution stops with an error, reject the gap.
4. Get the input of each failed unit test.
5. Run the original reference solution with these inputs. Record the result. This is the "original result".
6. Run the mutated solution with the same inputs. Record the result. This is the "alternative result".
7. Save the inputs, the original result, and the alternative result in the dataset item.

In Stage 2, a program does these steps:

1. Run the code of the agent with the saved inputs.
2. Compare the result with the two saved results:
   - If the result is the same as the original result, the agent used the original value.
   - If the result is the same as the alternative result, the agent used the alternative value.
   - If the result is different from the two saved results, the agent used a different value, or its code has an error.

### 6.3 Example: BigCodeBench/985

| Item | Content |
|---|---|
| Full instruction (part) | "If this function encounters a float population that is otherwise valid, it will round it down to the nearest integer." |
| Masked instruction (part) | "If this function encounters a float population that is otherwise valid, it will convert it to an integer." |
| Original value | Round down |
| Alternative value | Round to the nearest integer |
| Mutation | In the reference solution, change `math.floor(population)` to `round(population)` |

In Stage 1:

1. The gatekeeper runs the original unit tests on the mutated solution. Only `test_case_9` fails. All the other unit tests pass. Thus conditions (a) and (b) are true.
2. The input of `test_case_9` includes the population `1234567.89`.
3. The original reference solution gives `1234567`. This is the original result.
4. The mutated solution gives `1234568`. This is the alternative result.
5. The gatekeeper saves the input and the two results.

In Stage 2, the program runs the code of the agent with the population `1234567.89`:

- The result is `1234567`: the agent used "round down" (the original value).
- The result is `1234568`: the agent used "round to the nearest integer" (the alternative value).
- The result is a different value, or the code stops with an error: the agent used a different value, or its code has an error.

### 6.4 A second example: a gap that the procedure rejects

In BigCodeBench/889, the original value is "mean" and a possible alternative value is "median".

1. The gatekeeper runs the original unit tests on the mutated solution (median). All the unit tests pass, because each test column has only two numbers.
2. Thus condition (a) is not true. No unit test can show which value the agent used.
3. The gatekeeper rejects this gap, or labels it "untested" (see A6).

### 6.5 What we keep, what we lose, and what we get

**We keep:**

- Condition (a): proof that the gap changes the result of a unit test.
- Condition (b): proof that the mutation changes only the gap. All other requirements stay correct.

**We lose:**

- Conditions (c) and (d). But condition (b) already shows that the mutated solution is correct for all the other requirements. The saved results do the work of (c) and (d).

**We get:**

- The builder does not write test code. This removes the largest cause of errors.
- Stage 2 gets the program that finds which value the agent used (D3).

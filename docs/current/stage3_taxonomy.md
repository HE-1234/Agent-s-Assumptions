# Stage 3 (analysis): decision-type taxonomy (draft)

> **Status: draft, not in force.** This taxonomy is **not** given to any model that builds Stage 1 data. Builders get only the Stage 1 rules in `stage1_method.md`, so they are not asked to juggle extra categories. The taxonomy is applied **after** the dataset is built, to describe the gaps and to break down Stage 2 results (for example, RQ3 defaults by decision type).

## When and how labels are assigned

- **When:** after Stage 1 accepts a gap, before or after Stage 2 runs. The label never changes which gaps are built.
- **Who:** the owner, or a labeling model whose labels the owner spot-checks (report agreement).
- **What is recorded:** `decision_type` and `lhaw_dimension`, stored next to the dataset entry (not inside the Stage 1 builder output).
- **Templated sources:** for WorkBench and TravelPlanner, the label is assigned once per slot or field, not per item.

## Decision types

Each Stage 1 gap gets one **decision type**, assigned after the dataset is built. The taxonomy builds on LHAW ([arXiv 2602.10525](https://arxiv.org/abs/2602.10525), ICLR 2026), which removes information from clear agent tasks along four dimensions. We keep LHAW's dimensions as the top level and refine the one that holds almost all of our gaps.

**Top level (LHAW):**

| LHAW dimension | LHAW definition | In this study |
|---|---|---|
| Goal | The deliverable or success criteria are unclear | **Excluded.** Stage 1 never masks the goal ("the detail is the goal" fail rule) |
| Constraint | The rules, thresholds, or methods are unclear: the agent knows what to do but not the parameters | **Main dimension.** Refined into six decision types (below) |
| Input | The data source, file, system, or tool is unclear | **Reference** type |
| Context | Domain knowledge, jargon, or implicit requirements are unclear | **Reference** type when several real candidates fit; **Form** (out of scope) when only the packaging changes |

**Decision types.** LHAW's dimensions say what kind of information is missing. The types below say what the missing value decides. The refinement of Constraint is ours; each type has a membership test.

| Decision type | LHAW dimension | The choice decides… | Membership test | Examples |
|---|---|---|---|---|
| Scope | Constraint | Which items the task includes or acts on | Different values select a different set of items | Inclusive vs. exclusive end date; first vs. last column; include subfolders; "before 2" vs. "after 2"; case-sensitive matching |
| Edge-case policy | Constraint | What to do with irregular items | It matters only when missing, duplicate, tied, or bad input appears | Fill missing values with mean, median, or drop; keep first or last duplicate; on bad input, stop with an error or skip and continue |
| Method | Constraint | How the value is computed | The same inputs give different numbers | Round down vs. to nearest; absolute vs. signed correlation; Pearson vs. Spearman; mean vs. median; sampling with vs. without replacement |
| Magnitude | Constraint | How much, how long, how many | Values lie on one numeric scale | Meeting duration; "push back by 30 minutes"; number of items |
| Side effects | Constraint | What happens to existing state | Different values leave different state behind | Overwrite vs. append vs. skip an existing file; delete vs. archive |
| Preference | Constraint | Which category of thing the user wants | Distinct options chosen by taste or need | Room type; transport mode |
| Reference | Input, Context | What a term or input refers to | Several real candidates fit the words | Which "Raj" when two exist; time zone; units |

**Out of scope:**

| Excluded | Why |
|---|---|
| Form | Same content, different packaging (Stage 1 Test B removes these). Example: tuple vs. list, CSV vs. JSON, exception class name, fonts |
| Goal | LHAW's Goal dimension; removing it removes the task |
| *(not excluded)* Arbitrary identifiers | A new name, a threshold the user invents. Stage 1 allows them; label them **Reference** when several real candidates exist, otherwise **Magnitude** (numbers) or leave them unlabeled and report them as a group |
| Errors in the instruction; requests beyond the tools | Two of NoisyToolBench's four categories ([arXiv 2409.00557](https://arxiv.org/abs/2409.00557)). We study its other two: missing key information and multiple references |

"Stop with an error vs. skip and continue" is an Edge-case policy (in scope). "`TypeError` vs. `ValueError`" is Form (out of scope).

**Related taxonomies.**
- NoisyToolBench separates *missing key information* from *multiple references*. Our Reference type corresponds to the second.
- CLAMBER ([arXiv 2405.12063](https://arxiv.org/abs/2405.12063)) sorts output-changing gaps by Who, When, Where, and What. That overlaps our separate subject label (world / user / task), not our decision types.
- The multiverse-analysis literature lists the analysis choices that change results: which cases to exclude, how to transform or code variables, how to handle outliers (Steegen et al., 2016, [doi:10.1177/1745691616658637](https://doi.org/10.1177/1745691616658637); Wicherts et al., 2016, [doi:10.3389/fpsyg.2016.01832](https://doi.org/10.3389/fpsyg.2016.01832)). These support Scope, Method, and Edge-case policy.

**Validation, compared with LHAW.** LHAW labels each removed detail by running agents: *outcome-critical* (agents always fail), *divergent* (outcomes vary), or *benign* (agents reliably infer it). Stage 1's Test B plays the role of "not benign", but it is decided before any agent runs, so the dataset does not depend on the models it will test.

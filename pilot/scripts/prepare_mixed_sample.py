"""Build a benchmark-only OFFLINE construction walkthrough; no model calls or agent scores.

Run from the repository root: .venv/bin/python pilot/scripts/prepare_mixed_sample.py
Artifacts are deterministic and kept separate from the earlier Claude self-test.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import build_dataset as pipeline
import gatekeeper
from make_review import word_diff

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "pilot/runs/mixed_offline"


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def edit(before, after):
    """Smallest single contiguous edit, including enough context to be unique."""
    start = 0
    while start < min(len(before), len(after)) and before[start] == after[start]:
        start += 1
    end = 0
    while end < min(len(before), len(after)) - start and before[-end-1] == after[-end-1]:
        end += 1
    stop_a, stop_b = len(before)-end, len(after)-end
    while not before[start:stop_a] or before.count(before[start:stop_a]) != 1:
        if start:
            start -= 1
        elif stop_a < len(before):
            stop_a += 1
            stop_b += 1
        else:
            raise ValueError("no unique edit")
    return before[start:stop_a], after[start:stop_b]


def gap(seed, ident, variable, category, source, original, alternative, span, replacement,
        old_gold, new_gold, changed_tests, targets):
    old_test, new_test = edit(seed["tests"], changed_tests)
    return dict(subpart_id=ident, variable=variable, category=category, answer_source=source,
                is_crucial=True, original_value=original, alternative_values=[alternative],
                spans_removed=[span], replaced_with=[replacement], linked_decisions=targets,
                gold_solution_mutation=dict(find_in_gold=old_gold, replace_in_gold=new_gold,
                                            target_assertion=", ".join(targets)),
                test_mutation=dict(find_in_tests=old_test, replace_in_tests=new_test),
                target_tests=targets)


def coding_seeds():
    selected = {s["task_id"]: s for s in map(json.loads, (ROOT / "pilot/seeds.jsonl").read_text().splitlines())}
    seeds, builders = [], {}
    for sid in ("BigCodeBench/889", "BigCodeBench/985"):
        s = copy.deepcopy(selected[sid])
        s.update(domain="coding", provenance={"kind": "existing_benchmark", "source": "BigCodeBench v0.1.4",
                  "selection": "purposive: existing tested missing-value and rounding policies; not random"},
                 environment={}, user_facts={}, environment_bindings={}, extra_gaps=[])
        if sid.endswith("889"):
            tests = s["tests"].replace("27.5", "0.0").replace("55000.0", "0.0").replace("90.0", "0.0")
            sp = gap(s, "missing_values", "numeric_missing_value_policy", "Task", "User",
                     "column mean", "zero for partially observed columns",
                     "with the mean of the corresponding column", "using a fill policy",
                     "df[column].mean()", "(0 if df[column].notna().any() else np.nan)", tests,
                     ["test_numeric_columns_nan_replacement", "test_mixed_columns"])
            s["extra_gaps"] = [{"description": "All-NaN numeric columns: the full prompt does not explicitly specify what to do when the mean is undefined.",
                                 "found_by": "construction_author_review", "in_full_instruction": True}]
        else:
            tests = s["tests"].replace('"Population"].item(), 1234567\n', '"Population"].item(), 1234568\n')
            sp = gap(s, "rounding", "population_rounding", "Task", "User", "floor", "nearest integer",
                     "it will round it down to the nearest integer", "it will convert it to an integer",
                     "math.floor(population)", "round(population)", tests, ["test_case_9"])
            s["extra_gaps"] = [{"description": "The word 'empty' is underspecified: gold rejects {} but permits {'Countries': {}}. Preserve and flag the source mismatch.",
                                 "found_by": "construction_author_review", "in_full_instruction": True}]
        s["user_facts"][sp["variable"]] = sp["original_value"]
        seeds.append(s)
        builders[sid] = dict(status="ok", skip_reason="", candidate_subparts=[sp])
    return seeds, builders


def write_stage2_bundles(seed, main, directory):
    """Allowlisted views; this is a data boundary, not an OS sandbox."""
    neutral = ("You are an autonomous assistant completing a delegated task. You have access to environment tools, "
               "an `ask_user` tool to message the user, and a `submit` tool to deliver your final result. "
               "Complete the task and call `submit` with your final response to the user when finished.")
    tools = seed.get("tool_schemas_summary", pipeline.TOOLS_SUMMARY)
    runs = []
    for branch, online, instruction in (("A", None, main["masked_instruction"]),
            ("B-Full", True, seed["full_instruction"]), ("B-Online", True, main["masked_instruction"]),
            ("B-Offline", False, main["masked_instruction"])):
        path = directory / branch
        prompt = instruction
        if branch == "A":
            prompt += "\nBefore taking any action, list all unresolved choices or missing details in this task that could affect how you complete it."
        save(path / "agent_input.json", dict(system_prompt=neutral, instruction=prompt, tools_summary=tools,
             execution_allowed=branch != "A"))
        # A sees schemas only. Each B starts from a separate copy of initial state.
        if branch != "A":
            save(path / "world.json", seed["environment"])
            user_view = seed["full_instruction"]
            for ref in main["reference_ambiguities"]:
                if ref["answer_source"] == "World":
                    user_view, issues = gatekeeper.splice(user_view, [ref])
                    assert user_view is not None, issues
            save(path / "oracle_private.json", dict(online=online, user_view=user_view,
                 facts=seed["user_facts"], rules={
                    "specific_question": "Answer only the topic asked, using the user view. Never reveal unrelated facts.",
                    "broad_question": "Nothing specific comes to mind.",
                    "unknown": "I'm not sure—I haven't thought about that.",
                    "offline": "The user is currently offline and cannot reply.",
                    "confirmation": "Confirm only if the proposed action matches the user view; otherwise correct only the asked detail."}))
        runs.append(dict(branch=branch, status="not_run", agent_input=str((path / "agent_input.json").relative_to(OUT)),
                         fresh_session_required=True, world_access=branch != "A", user_online=online))
    save(directory / "grader_private.json", dict(reference_ambiguities=main["reference_ambiguities"],
         tests=seed["tests"], gold_solution=seed["gold_solution"], code_prompt=seed["code_prompt"]))
    return runs


def main():
    seeds, builders = coding_seeds()
    OUT.mkdir(parents=True, exist_ok=True)
    jsonl(OUT / "seeds.jsonl", seeds)
    save(OUT / "builder_fixtures.json", builders)
    entries, audits, runs = [], [], []
    for seed in seeds:
        sid = seed["task_id"]
        audit = pipeline.process_seed(seed, str(OUT), builders, False)
        assert audit["seed_status"] == "candidates_pending_check1", audit
        audit.update(source_provenance=seed["provenance"], world_absent_survival=[],
                     construction_source="author_prepared_masks_of_external_benchmark_seeds",
                     readable_reference_outputs=None)
        for entry in audit["entries"]:
            entry.update(domain=seed["domain"], provenance=seed["provenance"],
                         extra_gaps=seed["extra_gaps"], extra_gaps_status="author_review_only_not_blind")
            for ref in entry["reference_ambiguities"]:
                ref["label_provenance"] = dict(category="construction_author_assignment",
                    answer_source="proposed_harness_assignment_not_upstream_metadata", importance="test_run")
        save(OUT / "audit" / (sid.replace("/", "_") + ".json"), audit)
        entries.extend(audit["entries"])
        audits.append(audit)
        runs.extend(dict(seed_task_id=sid, **r) for r in write_stage2_bundles(
            seed, audit["entries"][-1], OUT / "stage2" / sid.replace("/", "_")))
        for entry in audit["entries"]:
            for ref in entry["reference_ambiguities"]:
                import random
                order = [ref["original_value"], ref["alternative_values"][0]]
                random.Random(f"{entry['task_id']}:{ref['subpart_id']}").shuffle(order)
                request = dict(system=pipeline.P.CHECK1_SYSTEM,
                    user=pipeline.P.fill(pipeline.P.CHECK1_USER, masked_instruction=entry["masked_instruction"],
                        variable_name=ref["variable"], value_option_1=order[0], value_option_2=order[1]),
                    schema=pipeline.P.CHECK1_SCHEMA)
                key = hashlib.sha256((entry["task_id"] + ref["subpart_id"]).encode()).hexdigest()[:12]
                save(OUT / "pending_check1" / (key + ".request.json"), request)
                save(OUT / "pending_check1_private" / (key + ".mapping.json"),
                     dict(task_id=entry["task_id"], subpart_id=ref["subpart_id"],
                          option_order=["original" if v == ref["original_value"] else "alternative" for v in order]))
    jsonl(OUT / "candidates.jsonl", entries)
    jsonl(OUT / "dataset.jsonl", [])
    save(OUT / "stage2_run_manifest.json", dict(status="prepared_not_executed", runs=runs,
         boundary="Only agent inputs and allowed tool data may enter agent context.",
         limitation="Review bundles are not an enforced sandbox."))
    first = seeds[0]
    diagnostic = gatekeeper.run_suite(first["code_prompt"] + first["gold_solution"].replace(
        "df[column].mean()", "df[column].median()"), first["tests"])
    save(OUT / "diagnostics.json", dict(mean_to_median=diagnostic,
         interpretation="Test undercoverage, not proof of a safe distractor."))
    manifest = dict(sample_design="benchmark-only purposive pilot; new external sources tracked separately",
        seeds=len(seeds), domain_counts={"coding": len(seeds)}, candidates=len(entries),
        unique_crucial_gaps=2, category_counts={"Task": 2}, answer_source_counts={"User": 2},
        finalized_entries=0, independent_model_calls=0, live_agent_runs=0, pending_blind_checks=2,
        atomic_decomposition="Selected maskable facts only, not exhaustive atomization.",
        source_hashes={s["task_id"]: hashlib.sha256(json.dumps(s, sort_keys=True).encode()).hexdigest() for s in seeds})
    save(OUT / "manifest.json", manifest)
    lines = ["# Benchmark-only offline construction review", "",
        "The assistant-authored task seeds and all their generated artifacts were removed at the user's request.",
        "Only existing BigCodeBench tasks are in this construction run. Imported replacement sources are tracked separately; no new tasks, reference answers, or graders were invented.", "",
        "2 seeds; 2 candidate variants; 2 test-verified gaps; 0 finalized entries. Required blind review is pending.", ""]
    for seed, audit in zip(seeds, audits):
        lines += ["## " + seed["task_id"], "", "````text", seed["full_instruction"], "````", ""]
        for result in audit["subparts"]:
            lines += ["### " + result["subpart"]["variable"], "", result["test_run"]["reason"], "",
                      "````diff", word_diff(seed["full_instruction"], result["masked_single"]), "````", ""]
        lines += [g["description"] for g in seed["extra_gaps"]]
    (OUT / "review.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

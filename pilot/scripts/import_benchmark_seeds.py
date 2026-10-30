"""Select unchanged published records; do not create masks, answers, or graders.

Sources must already be downloaded with source_index.json after dataset research.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = []
    specs = [
        ("workbench", "data/processed/tasks_and_outcomes/calendar_tasks_and_outcomes.csv", 61,
         "WorkBench/calendar-row-61", "workspace", "task", "outcome", "MIT",
         ["src/evals/evaluation.py", "src/evals/actions.py"],
         "First published calendar row with a create_event reference action; preliminary selection, not qualification.",
         "Requires the original state/tool dependencies and benchmark clock. No original evaluator execution or mask validation is claimed."),
        ("travelplanner", "train.csv", 18, "TravelPlanner/train-row-18", "planning", "query", "annotated_plan", "CC-BY-4.0",
         ["code/evaluation/hard_constraint.py", "code/evaluation/commonsense_constraint.py", "code/evaluation/eval.py"],
         "Training row previously identified in the dataset review; explicit private-room constraint and a source-provided annotated plan. Preliminary selection only.",
         "Full evaluation requires original travel databases and tool modules, which are not installed. Feasibility and distinguishing alternatives remain unaudited.")]
    for name, source_path, row_index, sid, domain, prompt_field, reference_field, license_name, graders, reason, limit in specs:
        root = ROOT / "data/raw" / name
        index = json.loads((root / "source_index.json").read_text())
        for entry in index["files"]:
            assert entry["status"] == "downloaded", entry
            assert hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"], entry["path"]
        rows = list(csv.DictReader((root / source_path).open()))
        row = rows[row_index]
        source = next(f for f in index["files"] if f["path"] == source_path)
        out.append(dict(task_id=sid, domain=domain, full_instruction=row[prompt_field], source_record=row,
            source_reference=row[reference_field], source_reference_field=reference_field,
            source_evaluators=[dict(path=p, content=(root / p).read_text(),
                source_url=next(f["source_url"] for f in index["files"] if f["path"] == p)) for p in graders],
            provenance=dict(kind="existing_benchmark", source=name, source_url=source["source_url"],
                revision=source["revision"], file_sha256=source["sha256"], row_index_zero_based=row_index,
                prompt_field=prompt_field, prompt_sha256=hashlib.sha256(row[prompt_field].encode()).hexdigest(),
                data_license=license_name, selection=reason, prompt_modified=False,
                reference_origin="upstream benchmark record", grader_origin="upstream benchmark code"),
            intake_status="imported_not_validated", validation=dict(original_grader="not_run",
                cruciality="not_run", leakage="not_run"), limitations=[limit],
            environment={}, environment_bindings={}, extra_gaps=[]))
    target = ROOT / "pilot/source_intake.jsonl"
    target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    print("Imported unchanged external records:", ", ".join(r["task_id"] for r in out))


if __name__ == "__main__":
    main()

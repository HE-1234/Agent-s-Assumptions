"""Write a factual, seed-ordered comparison of two completed Stage 1 runs."""
import argparse
import html
import json
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text())


def cell(value):
    return html.escape(str(value), quote=False).replace('|', '&#124;').replace('\n', '<br>')


def gap_text(part, stakes=False):
    sp = part['subpart']
    text = f"{sp['variable']}: {sp['original_value']} → {sp['alternative_values'][0]}"
    if stakes:
        text += '\nStakes: ' + sp['stakes']
    return text


def accepted(audit, stakes=False):
    parts = [gap_text(p, stakes) for p in audit['subparts'] if p['verdict'] == 'accepted']
    if parts:
        return '\n\n'.join(parts)
    if audit['seed_status'] == 'skipped_by_builder':
        return 'Builder skip: ' + audit['reason']
    return 'No accepted gaps. Seed status: ' + audit['seed_status']


def check1_rejections(audit):
    parts = []
    for p in audit['subparts']:
        if p.get('stopped_at') == 'G4' and p['verdict'] == 'rejected':
            check = p['leakage_check']
            parts.append(gap_text(p) + '\nG4: ' + p['reason']
                         + '\nReader choice: ' + check['reader_choice']
                         + '; confidence: ' + str(check['confidence'])
                         + '\nClue spans: ' + json.dumps(check['leftover_clue_spans'], ensure_ascii=False))
    return '\n\n'.join(parts) or 'None.'


def main(baseline, run_dir):
    if baseline.resolve() == run_dir.resolve():
        raise ValueError('Comparison output must be in a different run directory.')
    old, new = [read_json(p / 'summary.json') for p in (baseline, run_dir)]
    old_seeds, new_seeds = [(p / 'seeds.jsonl').read_bytes() for p in (baseline, run_dir)]
    if old_seeds != new_seeds:
        raise ValueError('Comparison requires identical seed files in the same order.')
    metrics = [
        ('Seeds with an accepted gap', ('seeds_with_accepted_gap',)),
        ('Gaps proposed', ('gaps', 'proposed')),
        ('Gaps accepted', ('gaps', 'accepted')),
        ('Builder skips', ('seeds', 'builder_skip_seed_task')),
        ('Check 1 fails', ('check1', 'fail')),
        ('Model calls (subagent invocations)', ('model_calls', 'count')),
        ('Wall clock (seconds)', ('wall_clock', 'total_s')),
    ]
    lines = ['# Pilot comparison', '', f'| Measure | {baseline.name} | {run_dir.name} |',
             '|---|---:|---:|']
    for label, keys in metrics:
        values = []
        for summary in (old, new):
            value = summary
            for key in keys:
                value = value[key]
            values.append(str(value))
        lines.append(f'| {label} | {values[0]} | {values[1]} |')
    lines += ['', 'Source: each run’s summary.json and per-seed audit files. Values, stakes sentences, skip reasons, and Check 1 results below are copied from those files. No quality judgments or owner overrides are applied.', '',
              'Both runs requested fresh GPT-6.1 Sol/high subagents. Token usage and provider-served model identity were unavailable in both runs.', '']
    for seed in map(json.loads, new_seeds.decode().splitlines()):
        sid = seed['task_id']
        audits = [read_json(p / 'audit' / (sid.replace('/', '_') + '.json')) for p in (baseline, run_dir)]
        lines += [f'## {sid}', '', f'| Result | {baseline.name} | {run_dir.name} |', '|---|---|---|',
                  f'| Accepted gaps / builder skip | {cell(accepted(audits[0]))} | {cell(accepted(audits[1], True))} |',
                  f'| Check 1 rejections | {cell(check1_rejections(audits[0]))} | {cell(check1_rejections(audits[1]))} |', '']
    output = run_dir / 'compare.md'
    output.write_text('\n'.join(lines))
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    main(args.baseline, args.run_dir)

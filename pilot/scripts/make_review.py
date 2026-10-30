"""Render v0 audit evidence and summary counts for the owner's review."""
import difflib
import json
from pathlib import Path
import re
import sys

FENCE = '``````'


def word_diff(original, masked):
    left, right = re.findall(r'\s+|\S+', original), re.findall(r'\s+|\S+', masked)
    output = []
    for tag, i, j, k, end in difflib.SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
        if tag == 'equal':
            output.extend(left[i:j])
        else:
            if i != j:
                output.append('[-' + ''.join(left[i:j]) + '-]')
            if k != end:
                output.append('{+' + ''.join(right[k:end]) + '+}')
    return ''.join(output)


def _flatten(value, prefix=''):
    for key, item in value.items():
        name = f'{prefix}.{key}' if prefix else key
        if isinstance(item, dict):
            yield from _flatten(item, name)
        else:
            yield name, item


def _explain(field):
    descriptions = {
        'fixture_only': 'True identifies an offline test whose accepted fixtures are excluded from the dataset.',
        'seeds.drawn': 'This is the number of input seeds.',
        'seeds.builder_ok': 'This counts seeds for which the builder returned ok.',
        'seeds.builder_skip_seed_task': 'This counts builder skip decisions.',
        'seeds.builder_error': 'This counts failed builder calls.',
        'seeds.needs_review': 'This counts seeds with unresolved cases recorded in QUESTIONS.md.',
        'seeds.budget_stopped': 'This counts seeds interrupted by an R7 limit.',
        'gaps.proposed': 'This counts every gap in the builder outputs.',
        'gaps.accepted': 'This counts gaps accepted by the gates, including test-only acceptance in fixture runs.',
        'gaps.needs_review': 'This counts gaps held for an owner decision.',
        'gaps.budget_stopped': 'This counts gaps interrupted by an R7 limit.',
        'seeds_with_accepted_gap': 'This counts seeds with at least one accepted gap.',
        'check1.pass': 'This counts reader responses with no clue spans.',
        'check1.prior_lean': 'This counts passes that chose a value without citing clues.',
        'check1.fail': 'This counts reader responses with any clue span.',
        'check1.skipped': 'This counts Check 1 omissions in offline tests.',
        'model_calls.count': 'This counts persisted model invocations in the unit recorded below.',
        'model_calls.count_unit': 'This distinguishes Codex subagent invocations from direct API attempts.',
        'model_calls.requested_models': 'These are the requested model configurations, not provider-confirmed served identities.',
        'model_calls.reasoning_efforts': 'These are the explicitly configured reasoning efforts.',
        'model_calls.usage_available': 'False means the transport did not expose token usage.',
        'model_calls.input_tokens': 'This sums reported input tokens; null means usage was unavailable.',
        'model_calls.output_tokens': 'This sums reported output tokens; null means usage was unavailable.',
        'model_calls.served_models': 'These are provider-reported served model names; an empty list means none were exposed.',
        'wall_clock.total_s': 'This is the elapsed time in seconds for this invocation.',
        'questions': 'This counts question entries in QUESTIONS.md.',
        'dataset_entries': 'This is the line count of dataset.jsonl; offline fixtures contribute no entries.',
        'rejected_records': 'This is the line count of rejected.jsonl, including rejected gaps and skipped or errored seeds.',
    }
    if field.startswith('gaps.stopped_at.'):
        return f"This counts gaps first rejected at {field.rsplit('.', 1)[1]}."
    if field.startswith('wall_clock.per_seed_stages.'):
        _, _, stage, statistic = field.split('.')
        return f"This is the {'median' if statistic == 'median_s' else 'maximum'} per-seed {stage} duration in seconds."
    return descriptions[field]


def main(run_dir, audits=None):
    directory = Path(run_dir)
    summary = json.loads((directory / 'summary.json').read_text())
    if audits is None:
        audits = [json.loads(path.read_text()) for path in sorted((directory / 'audit').glob('*.json'))]
    lines = ['# Stage 1 pilot v0 review', '', '| Field | Value | Reading guide |', '|---|---|---|']
    for field, value in _flatten(summary):
        lines.append(f'| {field} | {json.dumps(value)} | {_explain(field)} |')
    lines += ['', 'Diff notation: `[-removed-]` marks removed words and `{+inserted+}` marks replacement words.',
              'Original value is the hidden value in the full instruction.',
              'Alternative value is the single other value proposed by the builder.',
              'Reader choice is mapped back from shuffled option numbers to value labels and text.',
              'Confidence is the reader’s reported confidence, not a calibrated probability.',
              'Clue spans are the reader’s exact citations, with verbatim presence recorded.',
              'Surface flags are warnings for review and do not change the verdict.',
              'Owner verdict and Reason are blank fields for your keep/drop decision and explanation.', '']
    if summary['fixture_only']:
        lines += ['**OFFLINE TEST ONLY: Check 1 was skipped; no fixture is included in dataset.jsonl.**', '']
    for audit in audits:
        lines += [f"## {audit['task_id']} — {audit['seed_status']}", '']
        if audit.get('reason'):
            lines += [f"Reason: {audit['reason']}", '']
        if audit['seed_status'] == 'skipped_by_builder':
            lines += [FENCE + 'text', audit['full_instruction'], FENCE, '',
                      f"Builder skip reason: {audit['reason']}", '', 'Agree with skip (yes / no):', '']
        rejected = [part for part in audit['subparts'] if part['verdict'] != 'accepted']
        rejected.sort(key=lambda part: part.get('reason') != 'leakage')
        for part in rejected:
            lines.append(f"- {part['subpart'].get('subpart_id', '?')}: {part['stopped_at']} — "
                         f"{part['verdict']}: {part['reason']}; evidence: "
                         f"{json.dumps(part.get('evidence'), ensure_ascii=False)}")
            if part.get('reason') == 'leakage':
                lines += ['', f"Clue spans: {json.dumps(part['leakage_check']['clue_spans_checked'])}",
                          'Owner override (pass / keep rejection):', 'Override reason:', '']
        for part in audit['subparts']:
            if part['verdict'] != 'accepted':
                continue
            sp, check = part['subpart'], part['leakage_check']
            lines += ['', f"### {sp['subpart_id']} — {sp['variable']}", '',
                      f"Original value: {sp['original_value']}",
                      f"Alternative value: {sp['alternative_values'][0]}", '',
                      FENCE + 'text', word_diff(audit['full_instruction'], part['masked_single']), FENCE, '',
                      f"Check 1: {check['result']}; reader choice: {check.get('reader_choice', 'not run')}; "
                      f"value: {check.get('reader_value')}; confidence: {check.get('confidence')}; "
                      f"clue spans: {check.get('leftover_clue_spans', [])}; note: {check.get('note', '')}",
                      f"Option order: {check.get('option_order', [])}",
                      f"Clue verification: {check.get('clue_spans_checked', [])}",
                      f"Surface flags: {part.get('surface_flags', [])}", '',
                      'Owner verdict (keep / drop):', '', 'Reason:', '',
                      '- [ ] Is the removed detail a setting, not the goal of the task?',
                      '- [ ] Is the alternative realistic?',
                      '- [ ] Does the reference code really do what the instruction says for this detail?',
                      '- [ ] Would the two values lead to visibly different code or output?',
                      '- [ ] Does the masked text still read naturally?',
                      '- [ ] Is there a clue the reader missed?', '']
    (directory / 'review.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1])

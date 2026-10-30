"""Stage 1 v0: builder -> G1/G2/G3 -> Check 1/G4 -> audited single-gap entries.

Offline fixtures use --builder-json FILE --no-check1 and never enter dataset.jsonl.
"""
import argparse
import concurrent.futures as cf
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import statistics
import threading
import time
from zoneinfo import ZoneInfo

from jsonschema import validate, ValidationError
import gatekeeper as gk
import llm
from llm import LLMError, BudgetExceeded, call_json, write_json
import prompts as P

ROOT = Path(__file__).resolve().parents[2]
_question_lock = threading.Lock()


def note_question(run_dir, subject, happened):
    """R5: preserve the case, list options, and defer only the affected work."""
    path = Path(run_dir) / 'QUESTIONS.md'
    marker = hashlib.sha256(f'{subject}:{happened}'.encode()).hexdigest()
    with _question_lock:
        existing = path.read_text() if path.exists() else '# Questions\n'
        if marker in existing:
            return
        number = sum(line.startswith('## Q') for line in existing.splitlines()) + 1
        date = datetime.now(ZoneInfo('America/Los_Angeles')).date()
        path.write_text(existing + f'\n## Q{number} — {subject} ({date})\n\n'
                        f'<!-- {marker} -->\nWhat happened: {happened}\n\n'
                        'Options: the owner can define handling and rerun the affected item, '
                        'or leave it excluded pending review.\n\n'
                        'Meanwhile: marked the affected seed or gap needs_review, retained its evidence, '
                        'and continued unaffected work. No replacement rule or content retry was added.\n')


def run_builder(seed, run_dir, overrides):
    if overrides is not None:
        return overrides[seed['task_id']], {'tag': 'builder', 'source': 'fixture'}
    user = P.fill(P.BUILDER_USER, task_id=seed['task_id'],
                  full_instruction=seed['full_instruction'], gold_solution=seed['gold_solution'])
    return call_json(P.BUILDER_SYSTEM, user, P.BUILDER_SCHEMA,
                     Path(run_dir) / 'llm', f"builder.{seed['task_id'].replace('/', '_')}")


def run_check1(seed_id, sp, masked, run_dir):
    order = ['original_value', 'alternative_value']
    random.Random(f"{seed_id}:{sp['subpart_id']}").shuffle(order)
    values = {'original_value': sp['original_value'], 'alternative_value': sp['alternative_values'][0]}
    options = [values[label] for label in order]
    user = P.fill(P.CHECK1_USER, masked_instruction=masked, variable_name=sp['variable'],
                  value_option_1=options[0], value_option_2=options[1])
    parsed, rec = call_json(P.CHECK1_SYSTEM, user, P.CHECK1_SCHEMA,
                           Path(run_dir) / 'llm', f"check1.{seed_id.replace('/', '_')}.{sp['subpart_id']}")
    try:
        validate(parsed, P.CHECK1_SCHEMA)
    except ValidationError as error:
        raise gk.UncoveredCase(f'Check 1 response violates schema: {error.message}') from error
    return gk.check1_verdict(parsed, order, masked, options), rec


def make_entry(seed, result):
    sp = result['subpart']
    ref = {key: sp[key] for key in ('subpart_id', 'variable', 'spans_removed', 'replaced_with',
                                   'original_value', 'alternative_values')}
    check = result['leakage_check']
    leakage = {key: check[key] for key in ('result', 'reader_choice', 'option_order', 'leftover_clue_spans')}
    if 'note' in check:
        leakage['note'] = check['note']
    ref.update(answer_source='User', is_crucial=True, leakage_check=leakage)
    return {'task_id': f"{seed['task_id']}::single::{sp['variable']}",
            'seed_task_id': seed['task_id'],
            'source': {'benchmark': 'BigCodeBench', 'version': 'v0.1.4',
                       'instruction_sha256': hashlib.sha256(seed['full_instruction'].encode()).hexdigest()},
            'full_instruction': seed['full_instruction'], 'masked_instruction': result['masked_single'],
            'masking_mode': 'single_gap', 'reference_ambiguities': [ref], 'extra_gaps': [],
            'review': {'owner_verdict': None, 'owner_note': None}}


def _failure(result, gate, category, evidence):
    result['gates'].append({'gate': gate, 'result': 'fail', 'evidence': evidence})
    result.update(verdict='rejected', stopped_at=gate, reason=category, evidence=evidence)


def _process_seed(seed, run_dir, overrides, do_check1, audit):
    sid = seed['task_id']
    start = time.monotonic()
    try:
        built, rec = run_builder(seed, run_dir, overrides)
        audit['llm_calls'].append(rec)
    except LLMError as error:
        audit.update(seed_status='error', stopped_at='builder', reason=str(error),
                     failure_class=error.failure_class)
        if error.record:
            audit['llm_calls'].append(error.record)
        return
    finally:
        audit['timings_s']['builder'] = time.monotonic() - start
    audit['builder_output'] = built
    # Live builder schema failures follow G1.
    # Offline malformed fixtures still exercise their deliberately targeted gates.
    if overrides is None:
        try:
            validate(built, P.BUILDER_SCHEMA)
        except ValidationError as error:
            evidence = {'schema_error': error.message, 'path': list(error.absolute_path)}
            audit['gates'].append({'gate': 'G1', 'result': 'fail', 'evidence': evidence})
            audit.update(seed_status='skipped_by_builder', stopped_at='G1',
                         reason='Builder schema failure: ' + error.message)
            return
    if built['status'] != 'ok':
        audit['gates'].append({'gate': 'G1', 'result': 'fail', 'evidence': built})
        audit.update(seed_status='skipped_by_builder', stopped_at='G1', reason=built['skip_reason'])
        return
    audit['gates'].append({'gate': 'G1', 'result': 'pass', 'evidence': {'status': built['status']}})
    parts = built['candidate_subparts']
    if not parts or len(parts) > 3:
        raise gk.UncoveredCase(f'builder ok returned {len(parts)} gaps; expected a usable proposal of at most 3')
    seen_ids, seen_variables = set(), set()
    for sp in parts:
        result = {'subpart': sp, 'gates': [], 'surface_flags': []}
        audit['subparts'].append(result)
        gate = 'G2'
        try:
            issues = gk.malformed(sp)
            if issues:
                _failure(result, 'G2', 'malformed', issues)
                continue
            result['gates'].append({'gate': 'G2', 'result': 'pass', 'evidence': {
                'alternative_count': len(sp['alternative_values']),
                'span_count': len(sp['spans_removed']), 'replacement_count': len(sp['replaced_with'])}})
            gate = 'G3'
            start = time.monotonic()
            try:
                masked, issues = gk.splice(seed['full_instruction'], [sp])
            finally:
                elapsed = time.monotonic() - start
                audit['timings_s']['splice'] += elapsed
                result['splice_s'] = elapsed
            result['splice'] = {'ok': masked is not None, 'issues': issues}
            if masked is None:
                _failure(result, 'G3', 'splice', issues)
                continue
            result['gates'].append({'gate': 'G3', 'result': 'pass', 'evidence': result['splice']})
            result['masked_single'] = masked
            result['surface_flags'] = gk.surface_flags(masked, [sp]) + issues
            # Collisions cannot silently overwrite an entry or a Check 1 audit.
            if sp['subpart_id'] in seen_ids or sp['variable'] in seen_variables:
                raise gk.UncoveredCase('duplicate subpart_id or variable in builder output')
            seen_ids.add(sp['subpart_id'])
            seen_variables.add(sp['variable'])
            gate = 'G4'
            if do_check1:
                start = time.monotonic()
                try:
                    checked, rec = run_check1(sid, sp, masked, run_dir)
                    audit['llm_calls'].append(rec)
                finally:
                    elapsed = time.monotonic() - start
                    audit['timings_s']['check1'] += elapsed
                    result['check1_s'] = elapsed
                result['leakage_check'] = checked
                if checked['result'] == 'fail':
                    _failure(result, 'G4', 'leakage', checked)
                    continue
                result['gates'].append({'gate': 'G4', 'result': 'pass', 'evidence': checked})
            else:
                result['leakage_check'] = {'result': 'skipped', 'note': 'offline_fixture_only'}
                result['gates'].append({'gate': 'G4', 'result': 'skipped', 'evidence': 'Step 6 offline fixture'})
            result.update(verdict='accepted', stopped_at=None, reason='passed' if do_check1 else 'offline_fixture_only')
            if do_check1:
                audit['entries'].append(make_entry(seed, result))
        except BudgetExceeded as error:
            result.update(verdict='budget_stopped', stopped_at=gate, reason=str(error))
        except (LLMError, gk.UncoveredCase, KeyError, TypeError, ValueError) as error:
            result.update(verdict='needs_review', stopped_at=gate, reason=str(error))
            if isinstance(error, LLMError) and error.record:
                audit['llm_calls'].append(error.record)
            note_question(run_dir, f"{sid}/{sp.get('subpart_id', '?')}", str(error))
    statuses = [result['verdict'] for result in audit['subparts']]
    audit['seed_status'] = ('needs_review' if 'needs_review' in statuses else
                            'budget_stopped' if 'budget_stopped' in statuses else
                            'accepted' if 'accepted' in statuses else 'rejected')


def process_seed(seed, run_dir, overrides=None, do_check1=True):
    """Always persist an audit; fixtures can be accepted for tests but cannot become entries."""
    audit = {'task_id': seed['task_id'], 'full_instruction': seed['full_instruction'],
             'llm_calls': [], 'gates': [], 'subparts': [], 'entries': [],
             'fixture_only': not do_check1, 'timings_s': {'builder': 0, 'splice': 0, 'check1': 0}}
    try:
        _process_seed(seed, run_dir, overrides, do_check1, audit)
    except BudgetExceeded as error:
        audit.update(seed_status='budget_stopped', stopped_at='builder', reason=str(error))
    except (gk.UncoveredCase, KeyError, TypeError, ValueError) as error:
        audit.update(seed_status='needs_review', stopped_at='builder', reason=str(error))
        note_question(run_dir, seed['task_id'], str(error))
        # Keep evidence for every proposed gap even if the proposal cannot be processed.
        for sp in audit.get('builder_output', {}).get('candidate_subparts', []):
            if not any(result['subpart'] is sp for result in audit['subparts']):
                audit['subparts'].append({'subpart': sp, 'verdict': 'needs_review',
                                          'stopped_at': 'builder', 'reason': str(error), 'gates': []})
    path = Path(run_dir) / 'audit' / (seed['task_id'].replace('/', '_') + '.json')
    write_json(path, audit)
    return audit


def summarize(audits, run_dir, elapsed, fixture_only):
    parts = [part for audit in audits for part in audit['subparts']]
    checks = [part['leakage_check'] for part in parts if 'leakage_check' in part]
    attempts = [json.loads(path.read_text()) for path in (Path(run_dir) / 'llm').glob('attempt.*.json')]
    question_path = Path(run_dir) / 'QUESTIONS.md'
    questions = sum(line.startswith('## Q') for line in question_path.read_text().splitlines()) if question_path.exists() else 0
    builder_statuses = [audit.get('builder_output', {}).get('status') if isinstance(audit.get('builder_output'), dict) else None for audit in audits]
    stages = {}
    for stage in ('builder', 'splice', 'check1'):
        values = [audit['timings_s'][stage] for audit in audits]
        stages[stage] = {'median_s': statistics.median(values) if values else 0,
                         'max_s': max(values, default=0)}
    return {
        'fixture_only': fixture_only,
        'seeds': {'drawn': len(audits), 'builder_ok': sum(status == 'ok' and audit['seed_status'] != 'skipped_by_builder' for status, audit in zip(builder_statuses, audits)),
                  'builder_skip_seed_task': sum(audit['seed_status'] == 'skipped_by_builder' for audit in audits),
                  'builder_error': sum(audit['seed_status'] == 'error' for audit in audits),
                  'needs_review': sum(audit['seed_status'] == 'needs_review' for audit in audits),
                  'budget_stopped': sum(audit['seed_status'] == 'budget_stopped' for audit in audits)},
        'gaps': {'proposed': sum(len(audit['builder_output'].get('candidate_subparts', [])) for audit in audits if isinstance(audit.get('builder_output'), dict) and isinstance(audit['builder_output'].get('candidate_subparts', []), list)),
                 'stopped_at': {gate: sum(part.get('stopped_at') == gate and part['verdict'] == 'rejected' for part in parts)
                                for gate in ('G2', 'G3', 'G4')},
                 'accepted': sum(part['verdict'] == 'accepted' for part in parts),
                 'needs_review': sum(part['verdict'] == 'needs_review' for part in parts),
                 'budget_stopped': sum(part['verdict'] == 'budget_stopped' for part in parts)},
        'seeds_with_accepted_gap': sum(any(part['verdict'] == 'accepted' for part in audit['subparts']) for audit in audits),
        'check1': {'pass': sum(check['result'] == 'pass' for check in checks),
                   'prior_lean': sum(check.get('note') == 'prior_lean' for check in checks),
                   'fail': sum(check['result'] == 'fail' for check in checks),
                   'skipped': sum(check['result'] == 'skipped' for check in checks)},
        'model_calls': {'count': len(attempts),
                        'count_unit': 'subagent_invocations' if any(record.get('source') == 'codex_subagent' for record in attempts) else 'api_attempts',
                        'requested_models': sorted({record['requested_model'] for record in attempts if record.get('requested_model')}),
                        'reasoning_efforts': sorted({record['reasoning_effort'] for record in attempts if record.get('reasoning_effort')}),
                        'usage_available': all(record.get('usage_available', True) for record in attempts),
                        'input_tokens': None if any(record.get('usage_available') is False for record in attempts) else sum(record.get('usage', {}).get('input_tokens', 0) for record in attempts),
                        'output_tokens': None if any(record.get('usage_available') is False for record in attempts) else sum(record.get('usage', {}).get('output_tokens', 0) for record in attempts),
                        'served_models': sorted({record['served_model'] for record in attempts if record.get('served_model')})},
        'wall_clock': {'total_s': elapsed, 'per_seed_stages': stages}, 'questions': questions,
    }


def write_outputs(audits, run_dir, elapsed, fixture_only=False):
    directory = Path(run_dir)
    entries = [entry for audit in audits for entry in audit['entries']]
    rejected = []
    for audit in audits:
        if audit['seed_status'] in ('skipped_by_builder', 'error', 'needs_review', 'budget_stopped') and (
                not audit['subparts'] or audit.get('stopped_at') == 'builder'):
            rejected.append({'seed_task_id': audit['task_id'], 'status': audit['seed_status'],
                             'gate': audit.get('stopped_at'), 'reason': audit.get('reason')})
        for part in audit['subparts']:
            if part['verdict'] != 'accepted':
                rejected.append({'seed_task_id': audit['task_id'], 'subpart': part['subpart'],
                                 'status': part['verdict'], 'gate': part['stopped_at'],
                                 'reason': part['reason'], 'evidence': part.get('evidence'),
                                 'leakage_check': part.get('leakage_check')})
    for name, rows in [('dataset.jsonl', entries), ('rejected.jsonl', rejected)]:
        (directory / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    summary = summarize(audits, run_dir, elapsed, fixture_only)
    summary.update(dataset_entries=len(entries), rejected_records=len(rejected))
    write_json(directory / 'summary.json', summary)
    from make_review import main as make_review
    make_review(directory, audits=audits)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', default=str(ROOT / 'pilot/runs/pilot_v0/seeds.jsonl'))
    parser.add_argument('--run-dir', required=True)
    parser.add_argument('--builder-json', help='Complete offline fixture mapping; no fallback to a model')
    parser.add_argument('--no-check1', action='store_true')
    args = parser.parse_args(argv)
    seeds = [json.loads(line) for line in Path(args.seeds).read_text().splitlines()]
    overrides = json.loads(Path(args.builder_json).read_text()) if args.builder_json else None
    if args.no_check1 and overrides is None:
        parser.error('--no-check1 is for offline fixtures and requires --builder-json')
    if overrides is not None and any(seed['task_id'] not in overrides for seed in seeds):
        parser.error('--builder-json must cover every input seed; model fallback is disabled')
    if not args.no_check1:
        for name in ('PILOT_MODEL', 'OPENAI_API_KEY'):
            if not os.environ.get(name, '').strip():
                parser.error(f'{name} must be set; there is no default')
    directory = Path(args.run_dir)
    for child in ('audit', 'llm'):
        (directory / child).mkdir(parents=True, exist_ok=True)
    (directory / 'DEPARTURES.md').touch(exist_ok=True)
    start = time.monotonic()
    if not args.no_check1:
        llm.configure_run(directory / 'llm')
    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        audits = list(executor.map(lambda seed: process_seed(seed, directory, overrides, not args.no_check1), seeds))
    summary = write_outputs(audits, directory, time.monotonic() - start, args.no_check1)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    main()

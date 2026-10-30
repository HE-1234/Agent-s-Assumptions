"""Step 6 offline tests. Task code is opaque text; model calls are always mocked."""
import copy
import contextlib
import io
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import validate, ValidationError
import build_dataset as pipeline
import gatekeeper
import prompts
from select_seeds import RAW, RNG_SEED, seed_record

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'pilot/runs/pilot_v0'
TEST_OUTPUT = Path(os.environ.get('PILOT_TEST_OUTPUT_DIR', str(RUN)))
FIXTURES = Path(__file__).parent / 'fixtures/builder_v0.json'


def tiny_fixture():
    seed = {'task_id': 'synthetic', 'full_instruction': 'Round down. Keep this sentence.\ndef task_func(x):',
            'gold_solution': 'raise AssertionError("Task code must never execute")',
            'code_prompt': 'raise AssertionError("Task prompt must never execute")',
            'tests': 'raise AssertionError("Task tests must never execute")'}
    sp = {'subpart_id': 'gap_1', 'variable': 'rounding', 'original_value': 'down',
          'alternative_values': ['nearest'], 'spans_removed': ['Round down'], 'replaced_with': ['Convert']}
    return seed, sp


def builder(sp):
    return {'status': 'ok', 'skip_reason': '', 'candidate_subparts': [sp]}


def fake_reader(choice='3', clues=None):
    return {'choice': choice, 'confidence_0_to_1': 0.7, 'leftover_clue_spans': clues or []}, {'source': 'mock'}


class OfflineCase(unittest.TestCase):
    def setUp(self):
        TEST_OUTPUT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='test-', dir=TEST_OUTPUT)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.no_network = patch('llm.openai.AsyncOpenAI', side_effect=AssertionError('Live SDK forbidden in offline tests'))
        self.no_network.start()
        self.addCleanup(self.no_network.stop)

    def process(self, built, seed=None, do_check1=True, reader=None):
        seed = seed or tiny_fixture()[0]
        with patch.object(pipeline, 'call_json', return_value=reader or fake_reader()) as call:
            audit = pipeline.process_seed(seed, self.directory, {seed['task_id']: built}, do_check1)
        return audit, call


class SpliceTests(unittest.TestCase):
    def test_exact_replacement_and_untargeted_text(self):
        seed, sp = tiny_fixture()
        masked, flags = gatekeeper.splice(seed['full_instruction'], [sp])
        self.assertEqual(masked, 'Convert. Keep this sentence.\ndef task_func(x):')
        self.assertEqual(flags, [])

    def test_missing_span(self):
        seed, sp = tiny_fixture()
        sp['spans_removed'] = ['not in instruction']
        masked, issues = gatekeeper.splice(seed['full_instruction'], [sp])
        self.assertIsNone(masked)
        self.assertIn('not found', issues[0])

    def test_repeated_span_replaced_everywhere_and_flagged(self):
        _, sp = tiny_fixture()
        masked, issues = gatekeeper.splice('Round down. Then Round down.', [sp])
        self.assertEqual(masked, 'Convert. Then Convert.')
        self.assertIn('2x, all replaced', issues[0])

    def test_span_must_exist_in_original_not_only_in_replacement(self):
        _, sp = tiny_fixture()
        sp.update(spans_removed=['Round down', 'Convert'], replaced_with=['Convert', 'Other'])
        masked, issues = gatekeeper.splice('Round down.', [sp])
        self.assertIsNone(masked)
        self.assertIn('not found in full_instruction', issues[0])


class GateTests(OfflineCase):
    def test_g1_builder_skip_stops_before_gap_checks(self):
        built = {'status': 'skip_seed_task', 'skip_reason': 'No suitable setting', 'candidate_subparts': []}
        audit, call = self.process(built)
        self.assertEqual(audit['seed_status'], 'skipped_by_builder')
        self.assertEqual(audit['reason'], built['skip_reason'])
        self.assertEqual(audit['gates'][0]['gate'], 'G1')
        call.assert_not_called()

    def test_g2_two_alternatives_and_length_mismatch(self):
        for update in ({'alternative_values': ['nearest', 'up']}, {'replaced_with': []}):
            with self.subTest(update=update):
                _, sp = tiny_fixture()
                sp.update(update)
                audit, call = self.process(builder(sp))
                part = audit['subparts'][0]
                self.assertEqual((part['verdict'], part['stopped_at'], part['reason']), ('rejected', 'G2', 'malformed'))
                self.assertNotIn('splice', part)
                call.assert_not_called()

    def test_g3_missing_span_has_no_reader_call(self):
        _, sp = tiny_fixture()
        sp['spans_removed'] = ['not in instruction']
        audit, call = self.process(builder(sp))
        self.assertEqual(audit['subparts'][0]['stopped_at'], 'G3')
        self.assertEqual(audit['subparts'][0]['reason'], 'splice')
        call.assert_not_called()

    def test_accepted_single_gap_exact_dataset_schema_and_persisted_audit(self):
        seed, sp = tiny_fixture()
        audit, call = self.process(builder(sp))
        self.assertEqual(audit['seed_status'], 'accepted')
        self.assertEqual([gate['gate'] for gate in audit['subparts'][0]['gates']], ['G2', 'G3', 'G4'])
        self.assertEqual(len(audit['entries']), 1)
        entry = audit['entries'][0]
        self.assertEqual(set(entry), {'task_id', 'seed_task_id', 'source', 'full_instruction', 'masked_instruction',
                                      'masking_mode', 'reference_ambiguities', 'extra_gaps', 'review'})
        self.assertEqual(entry['task_id'], 'synthetic::single::rounding')
        ref = entry['reference_ambiguities'][0]
        self.assertEqual(set(ref), {'subpart_id', 'variable', 'spans_removed', 'replaced_with', 'answer_source',
                                    'is_crucial', 'original_value', 'alternative_values', 'leakage_check'})
        self.assertEqual(ref['answer_source'], 'User')
        self.assertIs(ref['is_crucial'], True)
        self.assertEqual(entry['source']['instruction_sha256'], hashlib.sha256(seed['full_instruction'].encode()).hexdigest())
        self.assertEqual(entry['extra_gaps'], [])
        self.assertEqual(entry['review'], {'owner_verdict': None, 'owner_note': None})
        call.assert_called_once()
        saved = json.loads((self.directory / 'audit/synthetic.json').read_text())
        saved_check = saved['subparts'][0]['leakage_check']
        self.assertEqual(set(ref['leakage_check']), {'result', 'reader_choice', 'option_order', 'leftover_clue_spans'})
        for key, value in ref['leakage_check'].items():
            self.assertEqual(saved_check[key], value)
        self.assertIn('confidence', saved_check)
        self.assertNotIn('run_tests', sys.modules)

    def test_g4_any_clue_rejects_even_when_not_verbatim(self):
        for clue, expected_presence in [('Keep this sentence.', True), ('invented clue', False)]:
            with self.subTest(clue=clue):
                _, sp = tiny_fixture()
                audit, call = self.process(builder(sp), reader=fake_reader('1', [clue]))
                part = audit['subparts'][0]
                self.assertEqual((part['verdict'], part['stopped_at'], part['reason']), ('rejected', 'G4', 'leakage'))
                self.assertEqual(part['leakage_check']['clue_spans_checked'][0]['present_in_masked'], expected_presence)
                self.assertEqual(audit['entries'], [])
                self.assertEqual(call.call_count, 1)

    def test_surface_flags_do_not_reject(self):
        seed, sp = tiny_fixture()
        seed['full_instruction'] += ' Downward default.'
        sp['original_value'] = 'Downward'
        audit, _ = self.process(builder(sp), seed=seed)
        self.assertTrue(audit['subparts'][0]['surface_flags'])
        self.assertEqual(audit['subparts'][0]['verdict'], 'accepted')

    def test_uncovered_gap_needs_review_and_other_gap_continues(self):
        _, sp = tiny_fixture()
        bad = copy.deepcopy(sp)
        bad.update(subpart_id='empty', variable='empty', spans_removed=[], replaced_with=[])
        built = builder(sp)
        built['candidate_subparts'].insert(0, bad)
        audit, _ = self.process(built)
        self.assertEqual([part['verdict'] for part in audit['subparts']], ['needs_review', 'accepted'])
        self.assertEqual(len(audit['entries']), 1)
        self.assertIn('empty spans_removed', (self.directory / 'QUESTIONS.md').read_text())

    def test_real_985_fixture_accepted_without_check1_but_not_dataset_entry(self):
        row = next(json.loads(line) for line in RAW.read_text().splitlines() if json.loads(line)['task_id'] == 'BigCodeBench/985')
        seed = seed_record(row)
        built = json.loads(FIXTURES.read_text())[seed['task_id']]
        audit, call = self.process(built, seed=seed, do_check1=False)
        part = audit['subparts'][0]
        self.assertEqual(part['verdict'], 'accepted')
        self.assertEqual(part['masked_single'], row['instruct_prompt'].replace(
            'round it down to the nearest integer', 'convert it to an integer'))
        self.assertEqual(part['leakage_check']['result'], 'skipped')
        self.assertEqual(audit['entries'], [])
        call.assert_not_called()

    def test_builder_uses_only_document_prompt_and_three_inputs(self):
        seed, _ = tiny_fixture()
        with patch.object(pipeline, 'call_json', return_value=({}, {})) as call:
            pipeline.run_builder(seed, self.directory, None)
        system, user, schema, _, _ = call.call_args.args
        self.assertEqual(system, prompts.BUILDER_SYSTEM)
        self.assertEqual(user, prompts.fill(prompts.BUILDER_USER, task_id=seed['task_id'],
                                            full_instruction=seed['full_instruction'], gold_solution=seed['gold_solution']))
        self.assertNotIn(seed['tests'], user)
        self.assertEqual(schema, prompts.BUILDER_SCHEMA)


class Check1Tests(OfflineCase):
    def test_both_option_orders_choices_prior_lean_and_full_signature(self):
        _, sp = tiny_fixture()
        seen = set()
        for index in range(30):
            sid = f'fixture/{index}'
            expected_order = ['original_value', 'alternative_value']
            random.Random(f"{sid}:{sp['subpart_id']}").shuffle(expected_order)
            seen.add(tuple(expected_order))
            for choice in ('1', '2', '3'):
                masked = 'Convert.\ndef task_func(x, policy="down"):'
                with patch.object(pipeline, 'call_json', return_value=fake_reader(choice)) as call:
                    result, _ = pipeline.run_check1(sid, sp, masked, self.directory)
                self.assertIn(masked, call.call_args.args[1])
                self.assertEqual(result['option_order'], expected_order)
                self.assertEqual(result['reader_choice'], expected_order[int(choice) - 1] if choice != '3' else 'undetermined')
                self.assertEqual(result.get('note'), 'prior_lean' if choice != '3' else None)
                self.assertEqual(result['result'], 'pass')
                if choice != '3':
                    self.assertEqual(result['reader_value'], 'down' if result['reader_choice'] == 'original_value' else 'nearest')
        self.assertEqual(len(seen), 2)


class PromptAndDrawTests(unittest.TestCase):
    def test_schema_accepts_fixture_and_skip_and_rejects_multiple_alternatives(self):
        built = json.loads(FIXTURES.read_text())['BigCodeBench/985']
        validate(built, prompts.BUILDER_SCHEMA)
        validate({'status': 'skip_seed_task', 'skip_reason': 'None', 'candidate_subparts': []}, prompts.BUILDER_SCHEMA)
        built['candidate_subparts'][0]['alternative_values'].append('reject floats')
        with self.assertRaises(ValidationError):
            validate(built, prompts.BUILDER_SCHEMA)

    def test_prompts_come_from_current_document_and_template_data_is_not_reprocessed(self):
        document = prompts.PROMPT_SOURCE.read_text()
        for system, user in [(prompts.BUILDER_SYSTEM, prompts.BUILDER_USER), (prompts.CHECK1_SYSTEM, prompts.CHECK1_USER)]:
            self.assertIn(system, document)
            self.assertIn(user, document)
        self.assertFalse(hasattr(prompts, 'PILOT_BUILDER_ADDENDUM'))
        self.assertEqual(prompts.fill('{{full_instruction}}', full_instruction='literal {{gold_solution}}'), 'literal {{gold_solution}}')

    def test_draw_is_unfiltered_reproducible_and_data_unchanged(self):
        rows = [json.loads(line) for line in RAW.read_text().splitlines()]
        self.assertEqual(len(rows), 1140)
        order = sorted((row['task_id'] for row in rows), key=lambda sid: int(sid.split('/')[1]))
        random.Random(RNG_SEED).shuffle(order)
        draw = json.loads((RUN / 'seed_draw.json').read_text())
        seeds = [json.loads(line) for line in (RUN / 'seeds.jsonl').read_text().splitlines()]
        self.assertEqual(draw, {'rng_seed': 20261029, 'shuffled_order': order})
        self.assertEqual([seed['task_id'] for seed in seeds], order[:20])
        by_id = {row['task_id']: row for row in rows}
        legacy = json.loads((ROOT / 'pilot/seeds.jsonl').read_text().splitlines()[0])
        for seed in seeds:
            self.assertEqual(seed, seed_record(by_id[seed['task_id']]))
            self.assertEqual(set(seed), set(legacy) - {'gold_check', 'why_picked'})


class OutputTests(OfflineCase):
    def test_rejected_counts_review_and_gate_evidence(self):
        seed, sp = tiny_fixture()
        audits = []
        for sid, update, reader in [
            ('accepted', {}, fake_reader()), ('malformed', {'alternative_values': ['a', 'b']}, fake_reader()),
            ('splice', {'spans_removed': ['absent']}, fake_reader()), ('leakage', {}, fake_reader('1', ['invented']))]:
            test_seed = {**seed, 'task_id': sid}
            test_part = {**sp, **update}
            audit, _ = self.process(builder(test_part), seed=test_seed, reader=reader)
            audits.append(audit)
        skipped, _ = self.process({'status': 'skip_seed_task', 'skip_reason': 'No parameter', 'candidate_subparts': []},
                                  seed={**seed, 'task_id': 'skipped'})
        audits.append(skipped)
        (self.directory / 'llm').mkdir()
        summary = pipeline.write_outputs(audits, self.directory, 0.5)
        self.assertEqual(summary['gaps']['stopped_at'], {'G2': 1, 'G3': 1, 'G4': 1})
        self.assertEqual(summary['gaps']['accepted'], 1)
        self.assertEqual(summary['dataset_entries'], 1)
        self.assertEqual(summary['rejected_records'], 4)
        self.assertEqual(len((self.directory / 'rejected.jsonl').read_text().splitlines()), 4)
        review = (self.directory / 'review.md').read_text()
        for text in ('Owner verdict (keep / drop):', 'Reason:', 'Agree with skip (yes / no):',
                     'Owner override (pass / keep rejection):', 'Original value:', 'Alternative value:'):
            self.assertIn(text, review)

    def test_offline_end_to_end_985_writes_step8_outputs_without_calls(self):
        # Keep this artifact as reviewable evidence, separately from the live seed draw.
        directory = TEST_OUTPUT / 'offline_fixture_985'
        directory.mkdir(exist_ok=True)
        row = next(json.loads(line) for line in RAW.read_text().splitlines() if json.loads(line)['task_id'] == 'BigCodeBench/985')
        seeds_path = directory / 'seeds.jsonl'
        seeds_path.write_text(json.dumps(seed_record(row)) + '\n')
        env = {key: value for key, value in os.environ.items() if key not in ('PILOT_MODEL', 'OPENAI_API_KEY')}
        command = ['uv', 'run', 'python', str(ROOT / 'pilot/scripts/build_dataset.py'), '--seeds', str(seeds_path),
                   '--run-dir', str(directory), '--builder-json', str(FIXTURES.resolve()), '--no-check1']
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('dataset.jsonl', 'rejected.jsonl', 'audit/BigCodeBench_985.json', 'llm',
                     'summary.json', 'review.md', 'DEPARTURES.md'):
            self.assertTrue((directory / name).exists(), name)
        summary = json.loads((directory / 'summary.json').read_text())
        self.assertEqual(summary['seeds']['drawn'], 1)
        self.assertEqual(summary['seeds']['builder_ok'], 1)
        self.assertEqual(summary['gaps']['proposed'], 1)
        self.assertEqual(summary['gaps']['accepted'], 1)
        self.assertEqual(summary['check1'], {'pass': 0, 'prior_lean': 0, 'fail': 0, 'skipped': 1})
        self.assertEqual(summary['model_calls']['count'], 0)
        self.assertEqual(summary['dataset_entries'], 0)
        self.assertEqual(summary['rejected_records'], 0)
        self.assertEqual((directory / 'dataset.jsonl').read_text(), '')
        self.assertEqual((directory / 'rejected.jsonl').read_text(), '')
        self.assertEqual(list((directory / 'llm').iterdir()), [])
        self.assertTrue(summary['fixture_only'])
        self.assertIn('OFFLINE TEST ONLY', (directory / 'review.md').read_text())

    def test_budget_stop_preserves_finished_gap_and_writes_outputs(self):
        seed, sp = tiny_fixture()
        second = copy.deepcopy(sp)
        second.update(subpart_id='gap_2', variable='other_rounding')
        built = builder(sp)
        built['candidate_subparts'].append(second)
        with patch.object(pipeline, 'call_json', side_effect=[fake_reader(), pipeline.BudgetExceeded('R7 call cap')]):
            audit = pipeline.process_seed(seed, self.directory, {seed['task_id']: built}, True)
        self.assertEqual(audit['seed_status'], 'budget_stopped')
        self.assertEqual([part['verdict'] for part in audit['subparts']], ['accepted', 'budget_stopped'])
        (self.directory / 'llm').mkdir()
        summary = pipeline.write_outputs([audit], self.directory, 1)
        self.assertEqual(summary['dataset_entries'], 1)
        self.assertEqual(summary['rejected_records'], 1)
        self.assertEqual(summary['gaps']['budget_stopped'], 1)
        self.assertTrue((self.directory / 'review.md').exists())

    def test_builder_error_is_a_rejected_seed_record(self):
        seed, _ = tiny_fixture()
        with patch.object(pipeline, 'call_json', side_effect=pipeline.LLMError('refusal', 'mock refusal')):
            audit = pipeline.process_seed(seed, self.directory)
        (self.directory / 'llm').mkdir()
        summary = pipeline.write_outputs([audit], self.directory, 1)
        self.assertEqual(summary['seeds']['builder_error'], 1)
        rejected = json.loads((self.directory / 'rejected.jsonl').read_text())
        self.assertEqual(rejected['gate'], 'builder')
        self.assertEqual(rejected['status'], 'error')
        self.assertEqual(summary['rejected_records'], 1)

    def test_incomplete_fixtures_cannot_fall_back_to_model(self):
        seeds = self.directory / 'seeds.jsonl'
        seeds.write_text(json.dumps(tiny_fixture()[0]) + '\n')
        fixtures = self.directory / 'builder.json'
        fixtures.write_text('{}')
        with contextlib.redirect_stderr(io.StringIO()), patch.object(pipeline, 'call_json') as call, self.assertRaises(SystemExit):
            pipeline.main(['--seeds', str(seeds), '--run-dir', str(self.directory),
                           '--builder-json', str(fixtures), '--no-check1'])
        call.assert_not_called()


if __name__ == '__main__':
    unittest.main()

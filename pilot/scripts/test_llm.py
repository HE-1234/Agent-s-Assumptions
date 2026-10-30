"""Offline tests: all SDK calls are mocked."""
import asyncio
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx2 as httpx
import openai
import llm

TEST_ROOT = Path(os.environ.get('PILOT_TEST_OUTPUT_DIR', str(Path(__file__).resolve().parents[1] / 'runs/pilot_v0')))


def temp_directory():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(prefix='test-client-', dir=TEST_ROOT)


SCHEMA = {'type': 'object', 'properties': {'ok': {'type': 'boolean'}},
          'required': ['ok'], 'additionalProperties': False}


def response(**updates):
    raw = {'model': 'mock-model-2026', 'status': 'completed',
           'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': '{"ok": true}'}]}],
           'usage': {'input_tokens': 11, 'output_tokens': 3}}
    raw.update(updates)
    value = MagicMock()
    value.model_dump.return_value = raw
    return value


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = temp_directory()
        self.addCleanup(self.temp.cleanup)
        self.directory = self.temp.name
        self.env = patch.dict(os.environ, PILOT_MODEL='mock-model', OPENAI_API_KEY='mock-key')
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = MagicMock()
        self.client.responses.create = AsyncMock(return_value=response())
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=self.client)
        context.__aexit__ = AsyncMock(return_value=False)
        self.sdk = patch.object(llm.openai, 'AsyncOpenAI', return_value=context)
        self.sdk.start()
        self.addCleanup(self.sdk.stop)

    def call(self, **kwargs):
        return llm.call_json('system', 'user', SCHEMA, self.directory, 'test', **kwargs)

    def test_mocked_sdk_cache_request_usage_and_import_without_key(self):
        parsed, rec = self.call()
        self.assertEqual(parsed, {'ok': True})
        self.assertEqual(rec['requested_model'], 'mock-model')
        self.assertEqual(rec['served_model'], 'mock-model-2026')
        self.assertEqual(rec['usage']['input_tokens'], 11)
        self.assertIn('latency_s', rec)
        request = self.client.responses.create.call_args.kwargs
        self.assertEqual(rec['request'], request)
        self.assertTrue(request['text']['format']['strict'])
        self.assertNotIn('temperature', request)
        self.assertNotIn('seed', request)
        self.assertTrue(self.call()[1]['cache_hit'])
        self.assertEqual(self.client.responses.create.call_count, 1)
        env = {k: v for k, v in os.environ.items() if k not in ('PILOT_MODEL', 'OPENAI_API_KEY')}
        result = subprocess.run([sys.executable, '-c', 'import llm'], env=env,
                                cwd=Path(llm.__file__).parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_config_is_clear(self):
        for name in ('PILOT_MODEL', 'OPENAI_API_KEY'):
            with patch.dict(os.environ, {name: ''}), self.assertRaisesRegex(llm.LLMError, name):
                self.call()
        self.client.responses.create.assert_not_called()

    def test_failure_classes_are_cached_without_content_retries(self):
        cases = [
            ('model_mismatch', {'model': 'another-model'}),
            ('refusal', {'output': [{'content': [{'type': 'refusal', 'refusal': 'no'}]}]}),
            ('truncated', {'status': 'incomplete', 'incomplete_details': {'reason': 'max_output_tokens'}}),
            ('api_error', {'output': [{'content': [{'type': 'output_text', 'text': 'invalid'}]}]}),
        ]
        for kind, updates in cases:
            with self.subTest(kind=kind), temp_directory() as directory:
                self.directory = directory
                self.client.responses.create.return_value = response(**updates)
                with self.assertRaises(llm.LLMError) as caught:
                    self.call()
                self.assertEqual(caught.exception.failure_class, kind)
                records = [json.loads(p.read_text()) for p in Path(directory).glob('attempt.*.json')]
                self.assertEqual(len(records), 1)
                self.assertIsNotNone(records[0]['response'])

    def test_transient_errors_retry_and_are_counted(self):
        req = httpx.Request('POST', 'https://api.openai.com/v1/responses')
        for error in [openai.APIConnectionError(request=req),
                      openai.RateLimitError('rate', response=httpx.Response(429, request=req), body={}),
                      openai.InternalServerError('server', response=httpx.Response(500, request=req), body={})]:
            with self.subTest(error=type(error).__name__), temp_directory() as directory:
                self.directory = directory
                self.client.responses.create.side_effect = [error, response()]
                with patch.object(llm.time, 'sleep'):
                    self.assertEqual(self.call()[1]['retries'], 1)
                self.assertEqual(len(list(Path(directory).glob('attempt.*.json'))), 2)

    def test_bad_request_does_not_retry(self):
        req = httpx.Request('POST', 'https://api.openai.com/v1/responses')
        self.client.responses.create.side_effect = openai.BadRequestError(
            'bad', response=httpx.Response(400, request=req), body={'error': 'bad schema'})
        with self.assertRaises(llm.LLMError):
            self.call()
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_hard_timeout(self):
        async def slow(**kwargs):
            await asyncio.sleep(1)
        self.client.responses.create.side_effect = slow
        with self.assertRaises(llm.LLMError) as caught:
            self.call(ceiling_s=0.01)
        self.assertEqual(caught.exception.failure_class, 'timeout')
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_parallel_call_cap_is_atomic(self):
        def invoke(index):
            try:
                return llm.call_json('system', f'user {index}', SCHEMA, self.directory, 'parallel')[0]
            except llm.BudgetExceeded:
                return 'stopped'
        with patch.object(llm, 'MAX_CALLS', 3):
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(invoke, range(12)))
        self.assertEqual(results.count('stopped'), 9)
        self.assertEqual(len(list(Path(self.directory).glob('attempt.*.json'))), 3)
        self.assertEqual(self.client.responses.create.call_count, 3)

    def test_persisted_call_cap_and_deadline(self):
        for index in range(100):
            (Path(self.directory) / f'attempt.{index + 1:03d}.json').write_text('{}')
        with self.assertRaises(llm.BudgetExceeded):
            self.call()
        self.client.responses.create.assert_not_called()
        with temp_directory() as directory:
            self.directory = directory
            with patch.object(llm, 'LIVE_SECONDS', -1):
                llm.configure_run(directory)
            with self.assertRaises(llm.BudgetExceeded):
                self.call()


if __name__ == '__main__':
    unittest.main()

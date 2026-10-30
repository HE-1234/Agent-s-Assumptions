"""Owner-authorized Codex subagent transport for the existing v0 pipeline.

The supervisor dispatches each request in a fresh GPT-6.1 Sol/high subagent,
with the exact document prompts and no tools, then supplies its raw final JSON.
No OpenAI API key is loaded. Token usage and served-model identity are unknown.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

import build_dataset as pipeline
import llm

ROOT = Path(__file__).resolve().parents[2]
RUN = None  # Required explicitly for every command; never default to a prior run.
MODEL = 'gpt-6.1-sol'
EFFORT = 'high'
_lock = threading.Lock()


def call_json(system, user, schema, cache_dir, tag):
    cache = Path(cache_dir)
    request = {'model': MODEL, 'reasoning_effort': EFFORT, 'fork_turns': 'none',
               'system': system, 'user': user, 'schema': schema,
               'transport': 'codex_subagent', 'tools_allowed': False}
    key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    finished = cache / f'{key}.json'
    if finished.exists():
        record = json.loads(finished.read_text())
        if record.get('failure_class'):
            raise llm.LLMError(record['failure_class'], record['error'], record)
        return record['parsed'], {**record, 'cache_hit': True}
    queued = RUN / 'subagent_requests' / f'{key}.json'
    started = time.time()
    deadline = started + min(600, llm.remaining_seconds(cache))
    llm.write_json(queued, {'key': key, 'tag': tag, 'request': request,
                           'queued_at': started, 'deadline': deadline})
    while time.time() < deadline:
        llm.remaining_seconds(cache)
        if finished.exists():
            record = json.loads(finished.read_text())
            if record.get('failure_class'):
                raise llm.LLMError(record['failure_class'], record['error'], record)
            return record['parsed'], record
        if len(list(cache.glob('attempt.*.json'))) >= llm.MAX_CALLS and not (RUN / 'subagent_requests' / f'{key}.dispatch.json').exists():
            raise llm.BudgetExceeded('R7: 100 subagent invocation limit reached')
        time.sleep(0.2)
    raise llm.LLMError('timeout', 'subagent request exceeded 600 seconds including queue time')


def next_job():
    for path in sorted((RUN / 'subagent_requests').glob('*.json'), key=lambda p: p.stat().st_mtime):
        if path.name.endswith('.dispatch.json'):
            continue
        job = json.loads(path.read_text())
        dispatch = path.with_name(job['key'] + '.dispatch.json')
        if dispatch.exists() or time.time() >= job['deadline']:
            continue
        # Each invocation gets the supplied prompts, never parent chat history.
        message = ('Complete this isolated text-only evaluation. Do not use tools, read files, run code, '
                   'or create agents. Return only the requested JSON.\n\nSYSTEM PROMPT:\n'
                   + job['request']['system'] + '\n\nUSER PROMPT:\n' + job['request']['user'])
        record = {'tag': job['tag'], 'content_hash': job['key'], 'requested_model': MODEL,
                  'configured_model': MODEL, 'served_model': None, 'reasoning_effort': EFFORT,
                  'source': 'codex_subagent', 'usage': {}, 'usage_available': False,
                  'request': job['request'], 'dispatch_message': message, 'status': 'started',
                  'dispatch_started_at': time.time(), 'response': None, 'latency_s': None}
        attempt = llm._reserve_attempt(RUN / 'llm', record)
        llm.write_json(dispatch, {'attempt_file': attempt.name, 'key': job['key']})
        print(json.dumps({'key': job['key'], 'tag': job['tag'], 'message': message, 'deadline': job['deadline']}))
        return
    print('null')


def finish(key, raw):
    dispatch = json.loads((RUN / 'subagent_requests' / f'{key}.dispatch.json').read_text())
    attempt_path = RUN / 'llm' / dispatch['attempt_file']
    record = json.loads(attempt_path.read_text())
    record.update(response=raw, latency_s=time.time() - record['dispatch_started_at'])
    try:
        record['parsed'] = json.loads(raw)
        record['status'] = 'completed'
    except json.JSONDecodeError as error:
        record.update(status='failed', failure_class='api_error', error=f'Invalid subagent JSON: {error}')
    llm.write_json(attempt_path, record)
    llm.write_json(RUN / 'llm' / f'{key}.json', record)
    print(json.dumps({'key': key, 'status': record['status']}))


def run(seeds_path=None):
    seeds = [json.loads(line) for line in (seeds_path or RUN / 'seeds.jsonl').read_text().splitlines()]
    for child in ('audit', 'llm', 'subagent_requests'):
        (RUN / child).mkdir(exist_ok=True)
    llm.configure_run(RUN / 'llm')
    started = time.monotonic()
    pipeline.call_json = call_json
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        audits = list(executor.map(lambda seed: pipeline.process_seed(seed, RUN, None, True), seeds))
    summary = pipeline.write_outputs(audits, RUN, time.monotonic() - started)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'next', 'finish'])
    parser.add_argument('key', nargs='?')
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--seeds', type=Path)
    args = parser.parse_args()
    RUN = args.run_dir.resolve()
    if RUN == (ROOT / 'pilot/runs/pilot_v0').resolve():
        parser.error('pilot_v0 is the protected baseline; choose a new run directory')
    if args.command == 'run':
        run(args.seeds)
    elif args.command == 'next':
        next_job()
    else:
        finish(args.key, sys.stdin.read())

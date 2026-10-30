"""Audited OpenAI Responses calls; importing this module never needs credentials."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import random
import threading
import time

import openai

MAX_CALLS = 100
LIVE_SECONDS = 60 * 60
_lock = threading.Lock()
_deadlines = {}


class LLMError(Exception):
    def __init__(self, failure_class, message, record=None):
        super().__init__(f"{failure_class}: {message}")
        self.failure_class = failure_class
        self.record = record


class BudgetExceeded(Exception):
    """R7 stopped the run; this is not a model failure."""


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def configure_run(cache_dir):
    """Start the live deadline; persisted attempt files enforce the call cap on resume."""
    with _lock:
        _deadlines[str(Path(cache_dir).resolve())] = time.monotonic() + LIVE_SECONDS


def remaining_seconds(cache_dir):
    deadline = _deadlines.get(str(Path(cache_dir).resolve()))
    remaining = deadline - time.monotonic() if deadline is not None else float('inf')
    if remaining <= 0:
        raise BudgetExceeded('R7: 60-minute live wall-clock limit reached')
    return remaining


def _reserve_attempt(cache_dir, record):
    directory = Path(cache_dir)
    with _lock:
        remaining_seconds(directory)
        directory.mkdir(parents=True, exist_ok=True)
        paths = list(directory.glob('attempt.*.json'))
        if len(paths) >= MAX_CALLS:
            raise BudgetExceeded('R7: 100 model-call limit reached (including retries)')
        path = directory / f'attempt.{len(paths) + 1:03d}.json'
        # Reserve before sending, so a crash cannot reset the count.
        write_json(path, record)
        return path


async def _request(request, ceiling_s):
    async with openai.AsyncOpenAI(max_retries=0, timeout=ceiling_s) as client:
        return await client.responses.create(**request)


async def _bounded_request(request, ceiling_s):
    return await asyncio.wait_for(_request(request, ceiling_s), timeout=ceiling_s)


def call_json(system, user, schema, cache_dir, tag, *, max_tokens=16000,
              ceiling_s=600, max_attempts=5):
    """Return (parsed, record), with complete requests/responses and no content retries."""
    for name in ('PILOT_MODEL', 'OPENAI_API_KEY'):
        if not os.environ.get(name, '').strip():
            raise LLMError('api_error', f'{name} must be set; there is no default')
    model = os.environ['PILOT_MODEL']
    request = {
        'model': model,
        'input': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'text': {'format': {'type': 'json_schema', 'name': 'pilot_output',
                            'strict': True, 'schema': schema}},
        'max_output_tokens': max_tokens,
    }
    key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    path = Path(cache_dir) / f'{key}.json'
    if path.exists():
        rec = json.loads(path.read_text())
        if rec.get('failure_class'):
            raise LLMError(rec['failure_class'], rec['error'], rec)
        return rec['parsed'], {**rec, 'cache_hit': True}

    started = time.monotonic()
    call_deadline = started + min(ceiling_s, remaining_seconds(cache_dir))
    attempt_paths = []
    for attempt in range(max_attempts):
        available = min(call_deadline - time.monotonic(), remaining_seconds(cache_dir))
        if available <= 0:
            raise LLMError('timeout', f'call exceeded {ceiling_s}s including retries')
        rec = {'tag': tag, 'content_hash': key, 'requested_model': model,
               'served_model': None, 'request': request, 'response': None,
               'usage': {}, 'latency_s': None, 'status': 'started',
               'client_parameters': {'max_retries': 0, 'timeout': available},
               'call_parameters': {'ceiling_s': ceiling_s, 'max_attempts': max_attempts},
               'attempt': attempt + 1}
        attempt_path = _reserve_attempt(cache_dir, rec)
        attempt_paths.append(attempt_path.name)
        attempt_started = time.monotonic()
        retryable = False
        try:
            response = asyncio.run(_bounded_request(request, available))
            raw = response.model_dump(mode='json')
            rec.update(response=raw, served_model=raw.get('model'), usage=raw.get('usage') or {})
            if not (raw.get('model') or '').startswith(model):
                raise LLMError('model_mismatch', f"asked {model}, served {raw.get('model')}")
            content = [part for item in raw.get('output', []) for part in item.get('content', [])]
            if any(part.get('type') == 'refusal' for part in content):
                raise LLMError('refusal', 'model refused; see raw response')
            if raw.get('status') == 'incomplete':
                details = raw.get('incomplete_details') or {}
                kind = 'refusal' if details.get('reason') == 'content_filter' else 'truncated'
                raise LLMError(kind, str(details))
            if raw.get('status') != 'completed':
                raise LLMError('api_error', f"response status {raw.get('status')}")
            text = ''.join(part['text'] for part in content if part.get('type') == 'output_text')
            try:
                rec['parsed'] = json.loads(text)
            except (ValueError, TypeError) as error:
                raise LLMError('api_error', 'invalid JSON response') from error
            rec['status'] = 'completed'
        except (TimeoutError, openai.APITimeoutError) as error:
            rec.update(status='failed', failure_class='timeout', error=type(error).__name__)
            retryable = isinstance(error, openai.APITimeoutError)
        except openai.APIError as error:
            retryable = (isinstance(error, (openai.RateLimitError, openai.APIConnectionError))
                         or isinstance(error, openai.APIStatusError) and error.status_code >= 500)
            rec.update(status='failed', failure_class='api_error', error=type(error).__name__)
            if isinstance(error, openai.APIStatusError):
                rec.update(http_status=error.status_code, response=error.body)
        except LLMError as error:
            rec.update(status='failed', failure_class=error.failure_class, error=str(error))
        rec['latency_s'] = round(time.monotonic() - attempt_started, 6)
        write_json(attempt_path, rec)
        aggregate = {**rec, 'attempt_files': attempt_paths,
                     'latency_s': round(time.monotonic() - started, 6), 'retries': attempt}
        if rec['status'] == 'completed':
            write_json(path, aggregate)
            return rec['parsed'], aggregate
        if retryable and attempt + 1 < max_attempts:
            delay = min(60, 2 ** (attempt + 1)) * (0.5 + random.random())
            available = min(call_deadline - time.monotonic(), remaining_seconds(cache_dir))
            if available > delay:
                time.sleep(delay)
                continue
        # Cache model/content failures, but leave transient failures retryable on crash resume.
        if not retryable:
            write_json(path, aggregate)
        raise LLMError(rec['failure_class'], rec['error'], aggregate)

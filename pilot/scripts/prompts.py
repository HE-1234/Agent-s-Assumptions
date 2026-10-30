"""Prompt text comes only from the owner's current Markdown document."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PROMPT_SOURCE = ROOT / 'docs/current/prompts_v0.md'


def _text_block_after(heading):
    markdown = PROMPT_SOURCE.read_text()
    section = markdown.split(heading + '\n', 1)[1].split('\n## ', 1)[0]
    match = re.search(r'```text\n(.*?)\n```', section, re.S)
    if match is None:
        raise ValueError(f'No text block under {heading}')
    system, user = match.group(1).split('USER PROMPT:\n', 1)
    return system.removeprefix('SYSTEM PROMPT:\n').strip(), user.strip()


BUILDER_SYSTEM, BUILDER_USER = _text_block_after('## Builder')
CHECK1_SYSTEM, CHECK1_USER = _text_block_after('## Check 1')


def _object(properties):
    return {'type': 'object', 'additionalProperties': False,
            'required': list(properties), 'properties': properties}


_STRING = {'type': 'string'}
_STRINGS = {'type': 'array', 'items': _STRING}
BUILDER_SCHEMA = _object({
    'status': {'type': 'string', 'enum': ['ok', 'skip_seed_task']},
    'skip_reason': _STRING,
    'candidate_subparts': {'type': 'array', 'maxItems': 3, 'items': _object({
        'subpart_id': _STRING,
        'variable': _STRING,
        'original_value': _STRING,
        'alternative_values': {**_STRINGS, 'minItems': 1, 'maxItems': 1},
        'spans_removed': _STRINGS,
        'replaced_with': _STRINGS,
    })},
})
CHECK1_SCHEMA = _object({
    'choice': {'type': 'string', 'enum': ['1', '2', '3']},
    'confidence_0_to_1': {'type': 'number'},
    'leftover_clue_spans': _STRINGS,
})


def fill(template, **values):
    # Substitute once: task text containing {{...}} is data, not another template.
    def substitute(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f'unfilled template variable: {key}')
        return str(values[key])
    return re.sub(r'\{\{(\w+)\}\}', substitute, template)

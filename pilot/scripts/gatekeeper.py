"""Deterministic v0 gates. No benchmark code is imported or executed."""
import json


class UncoveredCase(ValueError):
    """An input needs an owner decision under R5, rather than a new rejection rule."""


def malformed(sp):
    issues = []
    if len(sp['alternative_values']) != 1:
        issues.append('exactly one alternative value required')
    if len(sp['spans_removed']) != len(sp['replaced_with']):
        issues.append('spans_removed and replaced_with lengths differ')
    return issues


def splice(full_instruction, subparts):
    """Replace every occurrence of each exact span, in the builder's supplied order."""
    text, issues = full_instruction, []
    for sp in subparts:
        spans, replacements = sp['spans_removed'], sp['replaced_with']
        if len(spans) != len(replacements):
            return None, ['span/replacement lengths differ']
        if not spans or any(span == '' for span in spans):
            raise UncoveredCase('empty spans_removed list or empty-string span')
        for span, replacement in zip(spans, replacements):
            if span not in full_instruction:
                return None, [f"{sp['subpart_id']}: span not found in full_instruction: {span!r}"]
            count = text.count(span)
            if not count:
                return None, [f"{sp['subpart_id']}: splice failed; prior replacement consumed {span!r}"]
            if count > 1:
                issues.append(f"{sp['subpart_id']}: span occurs {count}x, all replaced: {span!r}")
            text = text.replace(span, replacement)
    if text == full_instruction:
        raise UncoveredCase('masking produced no change to the instruction')
    return text, issues


def surface_flags(masked, subparts):
    """Reviewer warnings only; these never change the verdict."""
    flags = []
    for sp in subparts:
        value = sp['original_value'].strip()
        if len(value) >= 4 and value.lower() in masked.lower():
            flags.append(f"{sp['subpart_id']}: original_value text still visible: {value!r}")
    if '  ' in masked.replace('\n    ', '\n'):
        flags.append('double space left by a cut')
    for bad in (' ,', ' .', ',,', '( )', '().'):
        if bad in masked:
            flags.append(f'punctuation artefact {bad!r}')
    return flags


def check1_verdict(parsed, option_order, masked, option_values):
    """Any clue fails, including clues absent verbatim; a clue-free pick is a prior lean."""
    choice = parsed['choice']
    clues = parsed['leftover_clue_spans']
    index = int(choice) - 1 if choice in ('1', '2') else None
    result = {'result': 'pass' if not clues else 'fail',
              'reader_choice': option_order[index] if index is not None else 'undetermined',
              'reader_value': option_values[index] if index is not None else None,
              'raw_choice': choice, 'option_order': option_order, 'option_values': option_values,
              'confidence': parsed['confidence_0_to_1'], 'leftover_clue_spans': clues,
              'clue_spans_checked': [{'span': clue, 'present_in_masked': clue in masked} for clue in clues]}
    if not clues and index is not None:
        result['note'] = 'prior_lean'
    return result


def dumps(value):
    return json.dumps(value, indent=2, ensure_ascii=False)

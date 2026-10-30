"""Step 2: unfiltered, reproducible draw. Benchmark code is only copied as text."""
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw/bigcodebench/v0.1.4.jsonl'
RUN = ROOT / 'pilot/runs/pilot_v0'
RNG_SEED = 20261029


def seed_record(row):
    return {'task_id': row['task_id'], 'full_instruction': row['instruct_prompt'],
            'code_prompt': row['code_prompt'], 'gold_solution': row['canonical_solution'],
            'tests': row['test'], 'libs': row['libs']}


def draw():
    rows = [json.loads(line) for line in RAW.read_text().splitlines()]
    by_id = {row['task_id']: row for row in rows}
    if len(rows) != 1140 or len(by_id) != 1140:
        raise ValueError('Step 2 requires exactly 1,140 unique BigCodeBench task IDs')
    order = sorted(by_id, key=lambda task_id: int(task_id.rsplit('/', 1)[1]))
    random.Random(RNG_SEED).shuffle(order)
    seeds = [seed_record(by_id[task_id]) for task_id in order[:20]]
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / 'seeds.jsonl').write_text(''.join(json.dumps(seed, ensure_ascii=False) + '\n' for seed in seeds))
    (RUN / 'seed_draw.json').write_text(json.dumps(
        {'rng_seed': RNG_SEED, 'shuffled_order': order}, indent=2) + '\n')
    print('\n'.join(seed['task_id'] for seed in seeds))


if __name__ == '__main__':
    draw()

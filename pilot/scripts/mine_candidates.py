"""Deterministic prefilter for BigCodeBench seed candidates (0 LLM calls).

Keeps tasks whose libs are all installable-light, and whose instruct_prompt
mentions at least one Stage-1 allowlist parameter type (companion guide 4.3).
"""
import ast, json, re, sys
import pandas as pd

LIGHT = {"random", "itertools", "collections", "json", "csv", "datetime", "re", "math",
         "statistics", "os", "string", "pandas", "numpy", "pytz", "dateutil", "time",
         "operator", "functools", "heapq", "io", "hashlib", "base64", "decimal"}
PATTERNS = {
    "timezone": r"\b(UTC|timezone|time zone|tz)\b",
    "rounding": r"\b(round(ed|ing)?|decimal places?)\b",
    "missing_values": r"\b(NaN|missing values?|None values?|null)\b",
    "duplicates": r"\bduplicate",
    "delimiter": r"\bdelimiter|separator\b",
    "sort_order": r"\b(sorted|ascending|descending|sort)\b",
    "encoding": r"\b(utf-8|encoding|latin)\b",
    "bad_input": r"\braise[sd]?\b.*\b(ValueError|TypeError|KeyError)\b",
    "output_format": r"\b(JSON|CSV|dict(ionary)?|list of tuples)\b",
}

df = pd.read_parquet(sys.argv[1])
rows = []
for _, r in df.iterrows():
    libs = set(ast.literal_eval(r["libs"]))  # stored as a str repr of a list
    if not libs <= LIGHT:
        continue
    text = r["instruct_prompt"]
    hits = [k for k, p in PATTERNS.items() if re.search(p, text, re.I)]
    if len(hits) >= 2:
        rows.append({"task_id": r["task_id"], "libs": sorted(libs), "hits": hits,
                     "n_words": len(text.split())})
print(json.dumps(rows))

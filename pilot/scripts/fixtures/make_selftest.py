"""Hand-written builder outputs with KNOWN correct verdicts, to test the gatekeeper offline."""
import json

def sp(i, *, spans, repl, find, replace, tests, tfind="", treplace="", crucial=True):
    return {"subpart_id": i, "variable": i, "category": "Task", "answer_source": "User",
            "is_crucial": crucial, "original_value": "orig " + i, "alternative_values": ["alt " + i],
            "spans_removed": spans, "replaced_with": repl, "linked_decisions": [],
            "gold_solution_mutation": {"find_in_gold": find, "replace_in_gold": replace,
                                       "target_assertion": ""},
            "target_tests": tests, "test_mutation": {"find_in_tests": tfind, "replace_in_tests": treplace}}

DEDUP = "    df = df.drop_duplicates(subset='Customer')\n"
EXP_DUP = "expected_output = {'Total Sales': 1200, 'Most Popular Category': 'Electronics'}"
fixture = {"BigCodeBench/232": {"status": "ok", "skip_reason": "", "candidate_subparts": [
    # EXPECT accepted, Crucial: counting duplicates gives 1400, only test_case_with_duplicates flips
    sp("oracle_dedup", spans=[", excluding duplicate customer names"], repl=[""],
       find=DEDUP, replace="", tests=["test_case_with_duplicates"],
       tfind=EXP_DUP, treplace=EXP_DUP.replace("1200", "1400")),
    # EXPECT rejected: no-op mutation
    sp("null_noop", spans=["total sales"], repl=["sales"], find="total_sales = df", replace="total_sales = df",
       tests=[]),
    # EXPECT rejected: span not in instruction
    sp("null_missing_span", spans=["excluding duplicate customers"], repl=[""], find=DEDUP,
       replace="", tests=["test_case_with_duplicates"]),
    # EXPECT rejected: breaks test_case_6, which is not in target_tests
    sp("null_unrelated", spans=["The report includes total sales"], repl=["The report includes sales"],
       find='raise ValueError("The input df', replace='raise TypeError("The input df',
       tests=["test_case_regular"]),
    # EXPECT accepted, Non-Crucial (builder said Crucial -> overridden): message text is never asserted
    sp("distractor_msg", spans=["The function will raise a ValueError is input df is not a DataFrame"],
       repl=["The function will raise a ValueError on bad input"],
       find="The input df is not a DataFrame", replace="Bad input", tests=[], crucial=True),
    # EXPECT needs_review: flip is real but test_mutation anchor does not exist
    sp("oracle_bad_testmut", spans=[", excluding duplicate customer names"], repl=[""],
       find=DEDUP, replace="", tests=["test_case_with_duplicates"],
       tfind="this string is not in the tests", treplace="x"),
]}}
json.dump(fixture, open("fixtures/selftest_232.json", "w"), indent=1)

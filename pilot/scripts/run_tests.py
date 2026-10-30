"""Run a BigCodeBench unittest suite against a solution in a subprocess.

Usage (library): run_suite(code_prompt + solution_body, test_code) -> dict
Returns per-test pass/fail so the gatekeeper can see WHICH assertion flipped.
"""
import json, os, subprocess, sys, tempfile, textwrap

HARNESS = textwrap.dedent('''
    import json, sys, unittest
    exec(compile(open(sys.argv[1]).read(), "solution", "exec"), globals())
    exec(compile(open(sys.argv[2]).read(), "tests", "exec"), globals())
    res = {}
    class R(unittest.TextTestResult):
        def addSuccess(self, t): super().addSuccess(t); res[t.id().split(".")[-1]] = "pass"
        def addFailure(self, t, e): super().addFailure(t, e); res[t.id().split(".")[-1]] = "fail"
        def addError(self, t, e): super().addError(t, e); res[t.id().split(".")[-1]] = "error"
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(resultclass=R, verbosity=0, stream=open("/dev/null", "w")).run(suite)
    print("__RESULT__" + json.dumps(res))
''')


def run_suite(solution: str, tests: str, timeout_s: int = 60) -> dict:
    with tempfile.TemporaryDirectory() as d:
        for name, body in (("sol.py", solution), ("tests.py", tests), ("h.py", HARNESS)):
            with open(os.path.join(d, name), "w") as f:
                f.write(body)
        try:
            p = subprocess.run([sys.executable, "-I", "h.py", "sol.py", "tests.py"], cwd=d,
                               capture_output=True, text=True, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "tests": {}}
        line = next((l for l in p.stdout.splitlines() if l.startswith("__RESULT__")), None)
        if line is None:
            return {"status": "crash", "tests": {}, "stderr": p.stderr[-2000:]}
        tests_res = json.loads(line[len("__RESULT__"):])
        ok = all(v == "pass" for v in tests_res.values()) and bool(tests_res)
        return {"status": "pass" if ok else "fail", "tests": tests_res}

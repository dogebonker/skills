import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import classify  # noqa: E402

RUBRIC = classify.RUBRIC_PATH.read_text(encoding="utf-8")


def inv(file, titles):
    return [{"id": f"{file}::{t}#0", "file": file, "lang": "ts", "title": t, "path": [t], "occurrence": 0,
             "start_byte": 0, "end_byte": 1, "start_line": i + 1, "end_line": i + 1, "kind": "test"}
            for i, t in enumerate(titles)]


class FakeLLM:
    """Answers each call with policy(call_index, ids) -> {id: verdict} or a raw object; records calls."""

    def __init__(self, policy, cost=0.01):
        self.policy, self.cost, self.calls = policy, cost, []

    def __call__(self, system, prompt, schema, model):
        ids = schema["properties"]["tests"]["items"]["properties"]["id"]["enum"]
        self.calls.append(ids)
        out = self.policy(len(self.calls) - 1, ids)
        if isinstance(out, dict) and "tests" not in out:
            cat = {"delete": "smoke", "keep": "protocol"}
            out = {"tests": [{"id": i, "verdict": v, "category": cat[v], "reason": f"r{len(self.calls)}"}
                             for i, v in out.items()]}
        return out, self.cost


class ClassifyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.test.ts").write_text("it('x', () => {})\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_classify(self, llm, tests, passes=1, cache=None, budget=None, fraction=1.0, concurrency=1, **kw):
        judge = classify.Judge(llm, "haiku", RUBRIC, cache, budget)
        rows = classify.classify(tests, self.repo, judge, passes, fraction, concurrency, **kw)
        return {r["id"]: r for r in rows}, judge

    def test_tools_are_preapproved_inside_the_repo_only(self):
        # an unscoped `Read` let a prompt-injected test file read outside the repo into the report
        from unittest import mock
        seen = {}
        def run(cmd, **kw):
            seen["cmd"] = cmd
            return mock.Mock(stdout=json.dumps({"structured_output": {}, "total_cost_usd": 0}), returncode=0)
        with mock.patch.object(classify.subprocess, "run", run):
            classify.claude_llm("s", "p", {}, "sonnet", tools="Read,Grep,Glob", cwd="/repo")
        cmd = seen["cmd"]
        self.assertEqual(cmd[cmd.index("--allowedTools") + 1], "Read(./**),Grep(./**),Glob(./**)")
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read,Grep,Glob")

    def test_rubric_categories(self):
        cats = classify.rubric_categories(RUBRIC)
        self.assertGreaterEqual(len(cats), 17)
        self.assertEqual(len(cats), len(set(cats)))
        self.assertIn("type-redundant", cats)
        self.assertIn("protocol", cats)

    def test_single_pass_takes_verdict(self):
        tests = inv("a.test.ts", ["a", "b"])
        llm = FakeLLM(lambda n, ids: {ids[0]: "delete", ids[1]: "keep"})
        rows, _ = self.run_classify(llm, tests)
        self.assertEqual(rows[tests[0]["id"]]["verdict"], "delete")
        self.assertEqual(rows[tests[0]["id"]]["category"], "smoke")
        self.assertEqual(rows[tests[1]["id"]]["votes"], ["keep"])
        self.assertEqual(len(llm.calls), 1)

    def test_double_pass_agreement_and_tiebreak(self):
        tests = inv("a.test.ts", ["agree-del", "agree-keep", "split"])
        a, k, s = (t["id"] for t in tests)
        answers = [{a: "delete", k: "keep", s: "delete"}, {a: "delete", k: "keep", s: "keep"}, {s: "delete"}]
        llm = FakeLLM(lambda n, ids: answers[n])
        rows, _ = self.run_classify(llm, tests, passes=2)
        self.assertEqual(rows[a]["verdict"], "delete")
        self.assertEqual(rows[a]["votes"], ["delete", "delete"])
        self.assertEqual(rows[k]["verdict"], "keep")
        self.assertEqual(rows[s]["verdict"], "delete")
        self.assertEqual(rows[s]["votes"], ["delete", "keep", "delete"])
        self.assertEqual(llm.calls[2], [s])  # tiebreak only judges the split tests

    def test_tiebreak_majority_keep(self):
        tests = inv("a.test.ts", ["split"])
        answers = ["delete", "keep", "keep"]
        rows, _ = self.run_classify(FakeLLM(lambda n, ids: {ids[0]: answers[n]}), tests, passes=2)
        self.assertEqual(rows[tests[0]["id"]]["verdict"], "keep")

    def test_double_fraction_zero_is_single_pass(self):
        tests = inv("a.test.ts", ["a"])
        llm = FakeLLM(lambda n, ids: {ids[0]: "delete"})
        rows, _ = self.run_classify(llm, tests, passes=2, fraction=0.0)
        self.assertEqual(len(llm.calls), 1)
        self.assertEqual(rows[tests[0]["id"]]["verdict"], "delete")

    def test_is_double_deterministic(self):
        picks = [classify.is_double(f"f{i}.ts", 0.5) for i in range(200)]
        self.assertEqual(picks, [classify.is_double(f"f{i}.ts", 0.5) for i in range(200)])
        self.assertTrue(40 < sum(picks) < 160)

    def test_missing_id_retries_then_succeeds(self):
        tests = inv("a.test.ts", ["a", "b"])
        llm = FakeLLM(lambda n, ids: {ids[0]: "delete"} if n == 0 else {i: "delete" for i in ids})
        rows, _ = self.run_classify(llm, tests)
        self.assertEqual(len(llm.calls), 2)
        self.assertEqual({r["verdict"] for r in rows.values()}, {"delete"})

    def test_fail_safe_keep_after_two_bad_outputs(self):
        tests = inv("a.test.ts", ["a", "b"])
        bad = [{"tests": "nope"}, None]
        llm = FakeLLM(lambda n, ids: bad[n])
        rows, _ = self.run_classify(llm, tests)
        self.assertEqual(len(llm.calls), 2)
        for r in rows.values():
            self.assertEqual((r["verdict"], r["category"]), ("keep", "classifier-error"))

    def test_crashing_llm_is_fail_safe(self):
        def boom(*_):
            raise RuntimeError("network")
        rows, _ = self.run_classify(boom, inv("a.test.ts", ["a"]))
        self.assertEqual(next(iter(rows.values()))["category"], "classifier-error")

    def test_validate_rejects_duplicates_unknown_and_bad_fields(self):
        ids, cats = {"x", "y"}, ["smoke"]
        row = lambda i, v="delete", c="smoke": {"id": i, "verdict": v, "category": c, "reason": ""}  # noqa: E731
        self.assertIsNotNone(classify.validate({"tests": [row("x"), row("y")]}, ids, cats))
        self.assertIsNone(classify.validate({"tests": [row("x"), row("x")]}, ids, cats))
        self.assertIsNone(classify.validate({"tests": [row("x"), row("z")]}, ids, cats))
        self.assertIsNone(classify.validate({"tests": [row("x"), row("y", v="maybe")]}, ids, cats))
        self.assertIsNone(classify.validate({"tests": [row("x"), row("y", c="other")]}, ids, cats))

    def test_cache_hit_makes_no_calls(self):
        tests = inv("a.test.ts", ["a"])
        with tempfile.TemporaryDirectory() as cache:
            llm = FakeLLM(lambda n, ids: {ids[0]: "delete"})
            first, _ = self.run_classify(llm, tests, passes=2, cache=cache)
            again = FakeLLM(lambda n, ids: {ids[0]: "keep"})
            second, judge = self.run_classify(again, tests, passes=2, cache=cache)
            self.assertEqual(again.calls, [])
            self.assertEqual(judge.spent, 0)
            self.assertEqual(first, second)
            (self.repo / "a.test.ts").write_text("changed\n")  # new content, new key
            self.run_classify(again, tests, passes=2, cache=cache)
            self.assertEqual(len(again.calls), 2)

    def test_failed_result_is_not_cached(self):
        tests = inv("a.test.ts", ["a"])
        with tempfile.TemporaryDirectory() as cache:
            self.run_classify(FakeLLM(lambda n, ids: None), tests, cache=cache)
            self.assertEqual(list(Path(cache).iterdir()), [])

    def test_budget_stops_new_calls(self):
        for f in ("b.test.ts", "c.test.ts"):
            (self.repo / f).write_text("x\n")
        tests = inv("a.test.ts", ["a"]) + inv("b.test.ts", ["b"]) + inv("c.test.ts", ["c"])
        llm = FakeLLM(lambda n, ids: {ids[0]: "delete"}, cost=0.5)
        rows, judge = self.run_classify(llm, tests, budget=0.4)
        self.assertEqual(len(llm.calls), 1)
        self.assertEqual(judge.spent, 0.5)
        cats = [rows[t["id"]]["category"] for t in tests]
        self.assertEqual(cats, ["smoke", "not-judged", "not-judged"])
        self.assertEqual(rows[tests[1]["id"]]["verdict"], "keep")

    def test_chunks_large_files_and_keeps_order(self):
        tests = inv("a.test.ts", [f"t{i}" for i in range(130)])
        llm = FakeLLM(lambda n, ids: {i: "keep" for i in ids})
        judge = classify.Judge(llm, "haiku", RUBRIC)
        rows = classify.classify(tests, self.repo, judge, 1, 0.0, 4)
        self.assertEqual(sorted(len(c) for c in llm.calls), [10, 60, 60])
        self.assertEqual([r["id"] for r in rows], [t["id"] for t in tests])

    def test_max_files(self):
        (self.repo / "b.test.ts").write_text("x\n")
        tests = inv("a.test.ts", ["a"]) + inv("b.test.ts", ["b"])
        llm = FakeLLM(lambda n, ids: {ids[0]: "delete"})
        rows, _ = self.run_classify(llm, tests, max_files=1)
        self.assertEqual(len(llm.calls), 1)
        self.assertEqual(rows[tests[1]["id"]]["category"], "not-judged")

    def test_main_writes_jsonl(self):
        tests = inv("a.test.ts", ["a"])
        inv_path = self.repo / "inventory.jsonl"
        inv_path.write_text("".join(json.dumps(t) + "\n" for t in tests))
        out = self.repo / "decisions.jsonl"
        orig = classify.claude_llm
        classify.claude_llm = FakeLLM(lambda n, ids: {ids[0]: "keep"})
        try:
            classify.main([str(inv_path), "--repo", str(self.repo), "-o", str(out), "--passes", "1",
                           "--cache", str(self.repo / "cache")])
        finally:
            classify.claude_llm = orig
        row = json.loads(out.read_text())
        self.assertEqual(set(row), {"id", "verdict", "category", "reason", "votes"})


if __name__ == "__main__":
    unittest.main()

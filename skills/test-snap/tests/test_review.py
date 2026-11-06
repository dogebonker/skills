import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import classify  # noqa: E402
import review  # noqa: E402

RUBRIC = classify.RUBRIC_PATH.read_text(encoding="utf-8")


def inv(file, titles):
    return [{"id": f"{file}::{t}#0", "file": file, "lang": "ts", "title": t, "path": [t], "occurrence": 0,
             "start_byte": 0, "end_byte": 1, "start_line": i + 1, "end_line": i + 1, "kind": "test"}
            for i, t in enumerate(titles)]


class FakeLLM:
    def __init__(self, policy, cost=0.1):
        self.policy, self.cost, self.calls = policy, cost, []

    def __call__(self, system, prompt, schema, model, **kw):
        ids = schema["properties"]["tests"]["items"]["properties"]["id"]["enum"]
        self.calls.append({"ids": ids, "prompt": prompt, "system": system, "kw": kw})
        out = self.policy(len(self.calls) - 1, ids)
        if isinstance(out, dict) and "tests" not in out:
            out = {"tests": [{"id": i, "verdict": v, "reason": "behavior x",
                              "covered_by": "b.test.ts" if v == "delete" else None,
                              "evidence": "it('x', () => {})" if v == "delete" else None} for i, v in out.items()]}
        return out, self.cost


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        for f in ("a.test.ts", "b.test.ts", "c.test.ts"):
            (self.repo / f).write_text("it('x', () => {})\n")
        self.inventory = inv("a.test.ts", ["r1", "r2", "k"]) + inv("c.test.ts", ["r3"])
        verdicts = ["review", "review", "keep", "review"]
        self.decisions = [{"id": t["id"], "verdict": v, "category": "smoke", "reason": "cls", "votes": ["delete"],
                           **({"guard": ["sole-guard:parse"]} if v == "review" else {})}
                          for t, v in zip(self.inventory, verdicts)]
        self.ids = [t["id"] for t in self.inventory]

    def tearDown(self):
        self.tmp.cleanup()

    def run_review(self, llm, cache=None, budget=None):
        judge = classify.Judge(llm, "sonnet", RUBRIC, cache, budget, system=review.reviewer_rubric(RUBRIC) + review.INSTRUCTIONS)
        return {r["id"]: r for r in review.review(self.inventory, self.decisions, self.repo, judge, 1)}, judge

    def test_resolves_review_rows_per_file_and_passes_others_through(self):
        llm = FakeLLM(lambda n, ids: {i: ("delete" if i.endswith("r1#0") else "keep") for i in ids})
        rows, _ = self.run_review(llm)
        self.assertEqual(sorted(len(c["ids"]) for c in llm.calls), [1, 2])  # one call per file
        r1 = rows[self.ids[0]]
        self.assertEqual((r1["verdict"], r1["covered_by"], r1["reason"]), ("delete", "b.test.ts", "behavior x"))
        self.assertEqual(r1["guard"], ["sole-guard:parse"])
        self.assertEqual(rows[self.ids[1]]["verdict"], "keep")
        self.assertEqual(rows[self.ids[2]], self.decisions[2])  # not in review: unchanged
        prompt = next(c["prompt"] for c in llm.calls if len(c["ids"]) == 2)
        self.assertIn("guard: sole-guard:parse", prompt)
        self.assertIn("classifier: smoke: cls", prompt)
        self.assertIn("## Review", llm.calls[0]["system"])
        self.assertNotIn("## Sensitive keywords", llm.calls[0]["system"])

    def test_failure_stays_review(self):
        rows, judge = self.run_review(FakeLLM(lambda n, ids: {"tests": []}))
        self.assertEqual(judge.calls, 4)  # one retry per file
        for i in (self.ids[0], self.ids[1], self.ids[3]):
            self.assertEqual((rows[i]["verdict"], rows[i]["review_note"]), ("review", "classifier-error"))

    def test_budget_leaves_rows_in_review(self):
        rows, judge = self.run_review(FakeLLM(lambda n, ids: {i: "delete" for i in ids}, cost=1.0), budget=0.5)
        self.assertEqual(judge.calls, 1)
        notes = sorted(rows[i].get("review_note", rows[i]["verdict"]) for i in (self.ids[0], self.ids[3]))
        self.assertEqual(notes, ["delete", "not-judged"])

    def write_tests(self, file, bodies):
        """Write a test file and return inventory rows with exact byte ranges for each body."""
        text, rows = "", []
        for i, body in enumerate(bodies):
            start = len(text.encode())
            text += body + "\n"
            rows.append({"id": f"{file}::t{i}#0", "file": file, "start_byte": start, "end_byte": len(text.encode())})
        (self.repo / file).write_text(text)
        return rows

    def test_enforce_requires_a_quote_inside_a_surviving_test(self):
        cover = self.write_tests("b.test.ts", ["it('covers', () => { expect(parse('9:00')).toBe(540) })"])
        own = self.write_tests("x.test.ts", ["it('x', () => { expect(parse('9:00')).toBe(540) })"])
        quote = "expect(parse('9:00')).toBe(540)"
        row = {"id": own[0]["id"], "verdict": "delete", "reason": "variant", "covered_by": "b.test.ts",
               "evidence": quote, "guard": ["fix-commit:abc fix: parse 9:00"]}

        def final(rows, inventory=cover + own):
            return [r["verdict"] for r in review.enforce_all(rows, inventory, self.repo)]

        self.assertEqual(final([row]), ["delete"])  # quoted line is inside a kept test
        self.assertEqual(final([{**row, "covered_by": "b.test.ts::covers"}]), ["delete"])  # test suffix ignored
        for bad in ({"covered_by": None}, {"covered_by": "missing.test.ts"}, {"evidence": None},
                    {"evidence": "expect(parse('10:00')).toBe(600)"}, {"evidence": "parse"}):
            self.assertEqual(final([{**row, **bad}]), ["keep"], bad)
        self.assertEqual(final([{**row, "evidence": "{\n   expect(parse('9:00'))"}]), ["delete"])  # whitespace
        # the cover names the very file being emptied, with a test suffix: nothing there survives
        emptied = {**row, "covered_by": "x.test.ts::x", "guard": ["sole-guard:parse", "empties:x.test.ts"]}
        self.assertEqual(final([emptied]), ["keep"])
        # the covering test is itself deleted: no cover survives
        cover_deleted = {"id": cover[0]["id"], "verdict": "delete", "reason": "", "covered_by": None}
        self.assertEqual(final([row, cover_deleted]), ["keep", "delete"])
        # two fix tests quoting each other both stay: neither cover survives the other's deletion
        pair = self.write_tests("p.test.ts", ["it('a', () => { expect(run('alpha-case')) })",
                                              "it('b', () => { expect(run('beta-case!')) })"])
        a = {**row, "id": pair[0]["id"], "covered_by": "p.test.ts", "evidence": "expect(run('beta-case!'))"}
        b = {**row, "id": pair[1]["id"], "covered_by": "p.test.ts", "evidence": "expect(run('alpha-case'))"}
        self.assertEqual(final([a, b], pair), ["keep", "keep"])
        # presentational delete with no fix commit and no emptied file needs no cover
        presentational = {**row, "covered_by": None, "evidence": None, "guard": ["sole-guard:parse"]}
        self.assertEqual(final([presentational]), ["delete"])
        self.assertEqual(final([{**presentational, "guard": ["sole-guard:parse", "empties:x.test.ts"]}]), ["keep"])
        unguarded = {k: v for k, v in presentational.items() if k != "guard"}
        self.assertEqual(final([unguarded]), ["delete"])  # never reviewed: untouched

    def test_validate(self):
        ok = {"id": "x", "verdict": "keep", "reason": "", "covered_by": None, "evidence": None}
        self.assertIsNotNone(review.validate({"tests": [ok]}, {"x"}))
        self.assertIsNone(review.validate({"tests": [ok, ok]}, {"x"}))
        self.assertIsNone(review.validate({"tests": [{**ok, "verdict": "review"}]}, {"x"}))
        self.assertIsNone(review.validate({"tests": [{**ok, "covered_by": 3}]}, {"x"}))
        self.assertIsNone(review.validate({"tests": []}, {"x"}))

    def test_cache_hit(self):
        with tempfile.TemporaryDirectory() as cache:
            self.run_review(FakeLLM(lambda n, ids: {i: "keep" for i in ids}), cache=cache)
            again = FakeLLM(lambda n, ids: {i: "delete" for i in ids})
            rows, _ = self.run_review(again, cache=cache)
        self.assertEqual(again.calls, [])
        self.assertEqual(rows[self.ids[0]]["verdict"], "keep")

    def test_main_runs_read_only_tools_in_repo(self):
        p = self.repo
        (p / "inv.jsonl").write_text("".join(json.dumps(t) + "\n" for t in self.inventory))
        (p / "dec.jsonl").write_text("".join(json.dumps(d) + "\n" for d in self.decisions))
        fake = FakeLLM(lambda n, ids: {i: "keep" for i in ids})
        orig = classify.claude_llm
        classify.claude_llm = fake
        try:
            review.main([str(p / "inv.jsonl"), str(p / "dec.jsonl"), "--repo", str(p), "-o", str(p / "out.jsonl"),
                         "--cache", str(p / "cache")])
        finally:
            classify.claude_llm = orig
        self.assertEqual(fake.calls[0]["kw"], {"tools": "Read,Grep,Glob", "cwd": str(p), "max_turns": 15})
        out = [json.loads(line) for line in (p / "out.jsonl").read_text().splitlines()]
        self.assertEqual([r["verdict"] for r in out], ["keep"] * 4)


if __name__ == "__main__":
    unittest.main()

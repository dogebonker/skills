import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import measure  # noqa: E402

SAMPLES = Path(__file__).resolve().parent / "samples"  # real output captured from each runner


def sample(name):
    return (SAMPLES / f"{name}.txt").read_text()


class ParseTest(unittest.TestCase):
    def check(self, text, runner, passed, failed, skipped, failures):
        r = measure.parse(text)
        self.assertEqual((r["runner"], r["passed"], r["failed"], r["skipped"]), (runner, passed, failed, skipped))
        self.assertEqual(r["failures"], failures)

    def test_vitest(self):
        self.check(sample("vitest"), "vitest", 1, 1, 1, ["a.test.ts > Math > breaks"])

    def test_vitest_with_ansi_and_workspaces(self):
        text = "\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[32m4 passed\x1b[39m\x1b[22m\x1b[90m (4)\x1b[39m\n"
        self.check(text + sample("vitest"), "vitest", 5, 1, 1, ["a.test.ts > Math > breaks"])

    def test_vitest_under_turbo_prefix(self):
        text = "".join(f"@scope/pkg:test: {line}\n" for line in sample("vitest").splitlines())
        self.check(text, "vitest", 1, 1, 1, ["a.test.ts > Math > breaks"])

    def test_pytest(self):
        self.check(sample("pytest"), "pytest", 1, 1, 1, ["test_a.py::test_fail"])

    def test_pytest_quiet_and_errors(self):
        text = "ERROR tests/test_b.py::test_x - RuntimeError\n2 failed, 7 passed, 1 error, 2 xfailed, 3 warnings in 1.20s\n"
        self.check(text, "pytest", 7, 3, 2, ["tests/test_b.py::test_x"])

    def test_cargo_sums_binaries(self):
        self.check(sample("cargo") * 2, "cargo", 2, 2, 2, ["tests::fails", "tests::fails"])

    def test_go_quiet(self):
        r = measure.parse(sample("go"))
        self.assertEqual((r["runner"], r["passed"], r["failed"], r["skipped"]), ("go", None, 2, None))
        self.assertEqual(r["failures"], ["TestFail", "TestFail/sub_one", "package example.com/demo"])
        self.assertEqual((r["packages_ok"], r["packages_failed"]), (0, 1))

    def test_go_verbose(self):
        self.check(sample("go_v"), "go", 1, 2, 1, ["TestFail", "TestFail/sub_one", "package example.com/demo"])

    def test_go_ok_packages(self):
        r = measure.parse("ok  \texample.com/a\t0.01s\nok  \texample.com/b\t(cached)\n?   \texample.com/c\t[no test files]\n")
        self.assertEqual((r["runner"], r["failed"], r["packages_ok"]), ("go", 0, 2))
        r = measure.parse("FAIL\texample.com/d [build failed]\n")
        self.assertEqual((r["runner"], r["failures"]), ("go", ["package example.com/d"]))

    def test_bun_sums_runs_and_names_load_errors(self):
        self.check(sample("bun") * 2, "bun", 2, 4, 4, ["b.test.ts > unhandled error", "a.test.ts > Math > breaks"] * 2)

    def test_unittest(self):
        self.check(sample("unittest"), "unittest", 1, 3, 2,
                   ["unittest.loader._FailedTest.test_a", "test_b.T.test_err", "test_b.T.test_bad"])

    def test_unittest_311_names_and_ok(self):
        text = "FAIL: test_bad (test_b.T.test_bad)\n\nRan 3 tests in 0.1s\n\nFAILED (failures=1)\nRan 4 tests in 0.2s\n\nOK\n"
        self.check(text, "unittest", 6, 1, 0, ["test_b.T.test_bad"])

    def test_node_tap(self):
        self.check(sample("node_tap"), "node", 1, 3, 1, ["breaks", "inner fails", "group"])

    def test_unknown_output(self):
        self.check("hello\n", None, None, None, None, [])


class RunCompareTest(unittest.TestCase):
    def test_run_records_exit_and_counts(self):
        with tempfile.TemporaryDirectory() as repo:
            r = measure.run(repo, f"cat '{SAMPLES / 'pytest.txt'}'; exit 3", 2)
        self.assertEqual(len(r["runs"]), 2)
        self.assertEqual(r["exit_code"], 3)
        self.assertEqual((r["runner"], r["failed"]), ("pytest", 1))
        json.dumps(r)

    def test_compare_separates_new_failures(self):
        before = {"wall_s": 10.0, "passed": 9, "failed": 1, "skipped": 0, "exit_code": 1, "failures": ["a"]}
        after = {"wall_s": 4.5, "passed": 5, "failed": 2, "skipped": 0, "exit_code": 1, "failures": ["a", "b"]}
        md = measure.compare_md(before, after)
        self.assertIn("| wall_s | 10.0 | 4.5 | -5.5 |", md)
        new, old = md.split("Pre-existing failures")
        self.assertIn("- b", new)
        self.assertNotIn("- a", new)
        self.assertIn("- a", old)

    def test_compare_cli(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ("b", "a"):
                Path(d, f"{name}.json").write_text(json.dumps({"wall_s": 1, "passed": None, "failures": []}))
            from contextlib import redirect_stdout
            from io import StringIO
            buf = StringIO()
            with redirect_stdout(buf):
                measure.main(["compare", str(Path(d, "b.json")), str(Path(d, "a.json"))])
        self.assertIn("| passed | n/a | n/a | n/a |", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

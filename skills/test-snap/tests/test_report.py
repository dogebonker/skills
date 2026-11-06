import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import report  # noqa: E402

INVENTORY = [{"id": f"{f}::{t}#0", "file": f, "title": t} for f, t in [
    ("apps/web/src/a.test.ts", "one"), ("apps/web/src/a.test.ts", "two"),
    ("apps/server/b.test.ts", "three"), ("tests/test_c.py", "four")]]
DECISIONS = [
    {"id": "apps/web/src/a.test.ts::one#0", "verdict": "delete", "category": "smoke", "reason": "mounts only"},
    {"id": "apps/web/src/a.test.ts::two#0", "verdict": "keep", "category": "protocol", "reason": "wire"},
    {"id": "apps/server/b.test.ts::three#0", "verdict": "review", "category": "smoke", "reason": "a | b",
     "guard": ["sensitive:token", "sole-guard:parse"]},
    {"id": "tests/test_c.py::four#0", "verdict": "delete", "category": "smoke", "reason": "defined",
     "guard": ["empties:tests/test_c.py"]},
]


class ReportTest(unittest.TestCase):
    def test_sections_and_counts(self):
        md = report.build(INVENTORY, DECISIONS)
        self.assertIn("4 tests inventoried in 3 files, 4 judged.", md)
        self.assertIn("| delete | 2 |", md)
        self.assertIn("| smoke | delete | 2 |", md)
        self.assertIn("| apps/web | 2 | 1 | 0 | 1 |", md)
        self.assertIn("| tests | 1 | 1 | 0 | 0 |", md)
        self.assertIn("## Review (2)", md)
        self.assertIn("| `apps/server/b.test.ts::three#0` | review | sensitive:token, sole-guard:parse | a \\| b |", md)
        self.assertIn("| `tests/test_c.py::four#0` | delete | empties:tests/test_c.py | defined |", md)
        self.assertNotIn("## Timing", md)
        self.assertNotIn("## Apply", md)

    def test_apply_and_timing(self):
        before = {"wall_s": 2.0, "passed": 4, "failed": 0, "skipped": 0, "exit_code": 0, "failures": []}
        after = {"wall_s": 1.0, "passed": 2, "failed": 0, "skipped": 0, "exit_code": 0, "failures": []}
        md = report.build(INVENTORY, DECISIONS, "deleted 2 tests\n", before, after)
        self.assertIn("```\ndeleted 2 tests\n```", md)
        self.assertIn("| wall_s | 2.0 | 1.0 | -1.0 |", md)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "inv.jsonl").write_text("".join(json.dumps(r) + "\n" for r in INVENTORY))
            (p / "dec.jsonl").write_text("".join(json.dumps(r) + "\n" for r in DECISIONS))
            report.main(["--inventory", str(p / "inv.jsonl"), "--decisions", str(p / "dec.jsonl"),
                         "-o", str(p / "r.md")])
            self.assertTrue((p / "r.md").read_text().startswith("# Test snap report"))


if __name__ == "__main__":
    unittest.main()

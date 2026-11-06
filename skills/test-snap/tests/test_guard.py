import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import guard  # noqa: E402

KEYWORDS = guard.sensitive_keywords(guard.RUBRIC_PATH.read_text(encoding="utf-8"))

TS = """import { describe, it, expect } from "vitest";
import { parseTotal, formatName } from "../src/cart";
import * as util from "../src/util";
import { render } from "@testing-library/react";
describe("cart", () => {
  it("parses total", () => { expect(parseTotal("1")).toBe(1); });
  it("formats name", () => { expect(formatName("a")).toBe("A"); });
  it("formats name again", () => { expect(formatName("b")).toBe("B"); });
  it("uses util", () => { expect(util.clamp(1)).toBe(1); });
  it("renders", () => { render(null); });
  it("refreshesToken", () => { expect(1).toBe(1); });
});
"""

PY = """import os
from os import path
import app.utils as au
from app.core import (
    slugify,  # the one under test
    titlecase,
)

def test_slug():
    assert slugify("A B") == "a-b"

def test_title():
    assert titlecase("a") == "A" and au.ok()

def test_paths():
    assert path.join("a", "b")
"""

RS = """pub fn add(a: i32, b: i32) -> i32 { a + b }

#[cfg(test)]
mod tests {
    use super::*;
    use crate::util::{clamp, wrap as wr};

    fn helper() -> i32 { 1 }

    #[test]
    fn adds() { assert_eq!(add(1, helper()), 2); }

    #[test]
    fn clamps() { assert_eq!(clamp(5), 3); }

    #[test]
    fn clamps_again() { assert_eq!(clamp(9), 3); }
}
"""

GO = """package foo_test

import (
\t"testing"

\t"example.com/m/foo"
\tr "github.com/stretchr/testify/require"
)

func TestParse(t *testing.T) { foo.Parse("x") }

func TestFormat(t *testing.T) { foo.Format("x") }

func TestFormatAgain(t *testing.T) { foo.Format("y"); r.Equal(t, 1, 1) }
"""

GO_SAME = """package foo

import "testing"

func TestDouble(t *testing.T) {
\tif Double(2) != 4 {
\t\tt.Fatal("bad")
\t}
}
"""


def tests_for(file, lang, src, marker_titles):
    """Inventory rows spanning from the marker line to the line end (ts) or the next blank line (others)."""
    raw = src.encode()
    rows = []
    for marker, title in marker_titles:
        start = raw.index(marker.encode())
        start = raw.rfind(b"\n", 0, start) + 1
        end = raw.find(b"\n" if lang == "ts" else b"\n\n", start)
        end = len(raw) if end == -1 else end
        rows.append({"id": f"{file}::{title}#0", "file": file, "lang": lang, "title": title, "path": [title],
                     "occurrence": 0, "start_byte": start, "end_byte": end, "start_line": 0, "end_line": 0,
                     "kind": "test"})
    return rows


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        files = {"web/cart.test.ts": TS, "tests/test_core.py": PY, "src/lib.rs": RS, "foo/foo_test.go": GO,
                 "foo/double_test.go": GO_SAME, "web/sessionStore.test.ts": TS}
        for f, src in files.items():
            (self.repo / f).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / f).write_text(src)
        self.inventory = (
            tests_for("web/cart.test.ts", "ts", TS, [(t, t) for t in (
                '"parses total"', '"formats name"', '"formats name again"', '"uses util"', '"renders"',
                '"refreshesToken"')])
            + tests_for("tests/test_core.py", "py", PY, [("def test_slug", "test_slug"),
                                                         ("def test_title", "test_title"),
                                                         ("def test_paths", "test_paths")])
            + tests_for("src/lib.rs", "rs", RS, [("fn adds", "adds"), ("fn clamps()", "clamps"),
                                                 ("fn clamps_again", "clamps_again")])
            + tests_for("foo/foo_test.go", "go", GO, [("func TestParse", "TestParse"),
                                                      ("func TestFormat(", "TestFormat"),
                                                      ("func TestFormatAgain", "TestFormatAgain")])
            + tests_for("foo/double_test.go", "go", GO_SAME, [("func TestDouble", "TestDouble")])
            + tests_for("web/sessionStore.test.ts", "ts", TS, [('"renders"', "renders")])
        )
        keep = {'web/cart.test.ts::"formats name"#0', "tests/test_core.py::test_title#0", "src/lib.rs::clamps#0",
                "foo/foo_test.go::TestFormat#0"}
        decisions = [{"id": t["id"], "verdict": "keep" if t["id"] in keep else "delete", "category": "smoke",
                      "reason": "r", "votes": ["delete"]} for t in self.inventory]
        self.rows = {r["id"]: r for r in guard.guard(self.inventory, decisions, self.repo, KEYWORDS)}

    def tearDown(self):
        self.tmp.cleanup()

    def guards(self, test_id):
        return self.rows[test_id].get("guard", [])

    def test_keywords_parsed_from_rubric(self):
        for k in ("auth", "token", "timezone", "ledger", "purge"):
            self.assertIn(k, KEYWORDS)
        self.assertGreater(len(KEYWORDS), 50)

    def test_word_parts_and_matching(self):
        self.assertEqual(guard.word_parts("web/sessionStore.test.ts"), ["web", "session", "store", "test", "ts"])
        self.assertEqual(guard.word_parts("parseHTTPHeader_value"), ["parse", "http", "header", "value"])
        hit = lambda title: guard.sensitive_hits({"file": "a.ts", "path": [title]}, KEYWORDS)  # noqa: E731
        self.assertEqual(hit("refreshes tokens"), ["token"])
        self.assertEqual(hit("tokenizer splits"), [])
        self.assertIn("permission", hit("checks Permissions"))

    def test_hard_words_keep_and_soft_words_review(self):
        self.assertEqual(KEYWORDS["token"], "hard")
        self.assertEqual(KEYWORDS["session"], "soft")
        self.assertEqual(self.guards('web/cart.test.ts::"refreshesToken"#0'), ["sensitive:token"])
        self.assertEqual(self.rows['web/cart.test.ts::"refreshesToken"#0']["verdict"], "keep")
        self.assertIn("sensitive:session", self.guards("web/sessionStore.test.ts::renders#0"))
        self.assertEqual(self.rows["web/sessionStore.test.ts::renders#0"]["verdict"], "review")

    def test_ts_sole_guard(self):
        self.assertEqual(self.guards('web/cart.test.ts::"parses total"#0'), ["sole-guard:parseTotal"])
        self.assertEqual(self.guards('web/cart.test.ts::"uses util"#0'), ["sole-guard:util.clamp"])
        self.assertEqual(self.rows['web/cart.test.ts::"formats name again"#0']["verdict"], "delete")
        self.assertEqual(self.rows['web/cart.test.ts::"renders"#0']["verdict"], "delete")  # testing-lib, not prod

    def test_python_sole_guard(self):
        self.assertEqual(self.guards("tests/test_core.py::test_slug#0"), ["sole-guard:slugify"])
        self.assertEqual(self.rows["tests/test_core.py::test_paths#0"]["verdict"], "delete")  # stdlib

    def test_rust_sole_guard(self):
        self.assertEqual(self.guards("src/lib.rs::adds#0"), ["sole-guard:add"])  # helper is local
        self.assertEqual(self.rows["src/lib.rs::clamps_again#0"]["verdict"], "delete")

    def test_go_sole_guard(self):
        self.assertEqual(self.guards("foo/foo_test.go::TestParse#0"), ["sole-guard:foo.Parse"])
        self.assertEqual(self.rows["foo/foo_test.go::TestFormatAgain#0"]["verdict"], "delete")
        self.assertEqual(self.guards("foo/double_test.go::TestDouble#0"),
                         ["sole-guard:Double", "empties:foo/double_test.go"])

    def test_keep_rows_untouched(self):
        row = self.rows['web/cart.test.ts::"formats name"#0']
        self.assertEqual(row["verdict"], "keep")
        self.assertNotIn("guard", row)

    def test_imports_per_language(self):
        ts = 'import Def, {\n  a,\n  type B,\n  c as d,\n} from "../x";\nimport type { T } from "./t";\n'
        self.assertEqual(guard.imports(ts, "ts"), ({"Def", "a", "B", "d", "T"}, set()))
        self.assertEqual(guard.imports("from .m import x, y as z\nimport pkg.sub\n", "py"),
                         ({"x", "z"}, {"pkg"}))
        self.assertEqual(guard.imports("use crate::a::x;\nuse super::b::{c, d::e};\nuse std::fmt;\n", "rs"),
                         ({"x", "c", "e"}, set()))
        self.assertEqual(guard.imports('import f "example.com/m/foo"\nimport "fmt"\n', "go"), (set(), {"f"}))


def row(file, path, lang="ts"):
    return {"id": f"{file}::{' > '.join(path)}#0", "file": file, "lang": lang, "title": path[-1], "path": path,
            "occurrence": 0, "start_byte": 0, "end_byte": 0, "start_line": 1, "end_line": 1, "kind": "test"}


class EmptiesTest(unittest.TestCase):
    def test_outermost_emptied_scope(self):
        inv = [row("x.ts", ["A", "t1"]), row("x.ts", ["A", "t2"]), row("x.ts", ["B", "C", "t3"]),
               row("x.ts", ["B", "t4"]), row("y.py", ["TestY", "test_5"], "py"),
               row("z_test.go", ["TestZ", "kept"], "go"), row("z_test.go", ["TestZ", "sub"], "go"),
               row("z_test.go", ["TestW", "only"], "go")]
        keep = {inv[1]["id"], inv[5]["id"]}
        decisions = [{"id": t["id"], "verdict": "keep" if t["id"] in keep else "delete"} for t in inv]
        with tempfile.TemporaryDirectory() as repo:
            for f in ("x.ts", "y.py", "z_test.go"):
                Path(repo, f).write_text("")
            rows = {r["id"]: r.get("guard", []) for r in guard.guard(inv, decisions, repo, [], history=False)}
        self.assertEqual(rows[inv[0]["id"]], [])  # A still has t2
        self.assertEqual(rows[inv[2]["id"]], ["empties:x.ts::B"])
        self.assertEqual(rows[inv[3]["id"]], ["empties:x.ts::B"])
        self.assertEqual(rows[inv[4]["id"]], ["empties:y.py"])
        self.assertEqual(rows[inv[6]["id"]], [])  # TestZ still has "kept"
        self.assertEqual(rows[inv[7]["id"]], ["empties:z_test.go::TestW"])  # Go parents are scopes, not tests


class FixCommitTest(unittest.TestCase):
    TITLES = ["plain add", 'handles "quoted" $(x) [a]*', "regression title", "issue title", "breaking title"]
    SUBJECTS = ["feat: add plain", "fix(api): quote handling", "chore: Regression for crash",
                "Fixes #12 crash", "hotfix!: urgent"]

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        body = ""
        for title, subject in zip(self.TITLES, self.SUBJECTS):
            body += "it('" + title + "', () => {});\n"
            Path(self.repo, "a.test.ts").write_text(body)
            self.git("add", "-A")
            self.git("commit", "-qm", subject)
        self.git("mv", "a.test.ts", "b.test.ts")
        self.git("commit", "-qm", "fix: rename that must not count")
        self.inv = [row("b.test.ts", [t]) for t in self.TITLES]

    def tearDown(self):
        self.tmp.cleanup()

    def test_is_fix(self):
        for s in ("fix: a", "fix(ui)!: a", "Bugfix: a", "test: regression for x", "Fix crash, closes #9"):
            self.assertTrue(guard.is_fix(s), s)
        for s in ("feat: a", "prefix: a", "closes #9", "chore: fixture update"):
            self.assertFalse(guard.is_fix(s), s)

    def test_fix_commits_follow_renames_and_odd_titles(self):
        found = guard.fix_commits(self.repo, self.inv)
        subjects = {i: c.split(" ", 1)[1] for i, c in found.items()}
        self.assertEqual(subjects, {t["id"]: s for t, s in zip(self.inv, self.SUBJECTS) if s != "feat: add plain"})

    def test_guard_flags_and_respects_no_history(self):
        decisions = [{"id": t["id"], "verdict": "delete"} for t in self.inv]
        rows = guard.guard(self.inv, decisions, self.repo, [])
        self.assertTrue(rows[1]["guard"][-1].startswith("fix-commit:"))
        self.assertTrue(rows[1]["guard"][-1].endswith(" fix(api): quote handling"))
        self.assertFalse(any(g.startswith("fix-commit:") for g in rows[0]["guard"]))
        self.assertEqual(rows[1]["verdict"], "review")  # fix tests go to the reviewer
        self.assertNotEqual(rows[0]["verdict"], "keep")
        rows = guard.guard(self.inv, decisions, self.repo, [], history=False)
        self.assertFalse(any(g.startswith("fix-commit:") for r in rows for g in r["guard"]))

    def test_outside_git_is_silent(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertEqual(guard.fix_commits(plain, self.inv), {})


if __name__ == "__main__":
    unittest.main()

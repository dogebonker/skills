import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import apply  # noqa: E402
import astgrep  # noqa: E402
import inventory  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
DELETE = [
    # ts: one of two duplicate titles, an .each, a todo, and the only test of a describe
    "ts/cart.test.ts::Cart > add > adds an item#0",
    "ts/cart.test.ts::Cart > add > adds %i units#0",
    "ts/cart.test.ts::Cart > supports gift cards#0",
    "ts/cart.test.ts::Empty after delete > is the only test here#0",
    "ts/session.test.ts::with session layer > nested layer > still works#0",
    "ts/crlf.test.ts::crlf > second#0",
    # a file with spurious tree-sitter errors: edited, not reverted, its describe kept
    "ts/mocked.test.ts::mocked fs > sees the mock#0",
    # every test of the file: the file goes
    "ts/Button.browser.test.tsx::Button > renders the label#0",
    "ts/Button.browser.test.tsx::Button > calls onClick#0",
    # py: a whole Test class (setup only left), a TestCase, a decorated test, a class that keeps its base
    "py/test_ledger.py::test_deposit#0",
    "py/test_ledger.py::TestWithdraw > test_withdraw#0",
    "py/test_ledger.py::TestWithdraw > test_withdraw_too_much#0",
    "py/test_ledger.py::TestWithdraw > TestNested > test_inner#0",
    "py/test_ledger.py::LedgerCase > test_repr#0",
    "py/test_ledger.py::TestPostgresStorage > test_pg_only#0",
    "py/test_crlf.py::test_two#0",
    # rs: a nested mod emptied, attributes and docs go with their fn; a tests/ file emptied
    "rs/src/lib.rs::tests > rejects_missing_unit#0",
    "rs/src/lib.rs::tests > parses_cases#0",
    "rs/src/lib.rs::tests > nested > inner#0",
    "rs/tests/integration.rs::parses_from_setup#0",
    "rs/tests/integration.rs::parses_zero#0",
    # go: nested subtests, a doc-commented test, a file with only one test, a file that keeps a helper
    "go/calc_test.go::TestParse > invalid > empty#0",
    "go/calc_test.go::TestParse > invalid > letters ü#0",
    "go/calc_test.go::TestAdd#0",
    "go/only_test.go::TestOnly#0",
    "go/helpers_test.go::TestMustParse#0",
]


def read(root, rel):
    with open(os.path.join(root, rel), "rb") as f:
        return f.read()


class ApplyFixturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="test-snap-apply-")
        shutil.copytree(FIXTURES, cls.root, dirs_exist_ok=True)
        files = inventory.find_files(cls.root)
        result, _ = inventory.extract(cls.root, files)
        cls.inv = [t for rel in sorted(result) for t in result[rel][0]]
        ids = {t["id"] for t in cls.inv}
        assert set(DELETE) <= ids, set(DELETE) - ids
        decisions = [{"id": t["id"], "verdict": "delete" if t["id"] in DELETE else "keep"} for t in cls.inv]
        cls.out = apply.apply(cls.inv, decisions, cls.root, run_cleanup=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def test_summary(self):
        self.assertEqual(self.out["reverted"], [])
        self.assertEqual(sorted(self.out["deleted"]), ["go/only_test.go", "rs/tests/integration.rs",
                                                       "ts/Button.browser.test.tsx"])
        self.assertEqual(self.out["tests_deleted"], len(DELETE))
        self.assertIn("tests deleted: %d" % len(DELETE), self.out["lines"])

    def test_edited_files_still_parse(self):
        paths = [os.path.join(self.root, rel) for rel in self.out["edited"]]
        self.assertEqual(len(paths), 9)
        errors = list(astgrep.scan(apply.ERR_RULES, paths))
        self.assertEqual({os.path.basename(m["file"]) for m in errors}, {"mocked.test.ts"})  # pre-existing only
        for rel in self.out["edited"]:
            if rel.endswith(".py"):
                self.assertTrue(inventory.py_compiles(read(self.root, rel), rel), rel)

    @unittest.skipUnless(shutil.which("gofmt"), "gofmt not installed")
    def test_go_files_pass_gofmt(self):
        r = subprocess.run(["gofmt", "-l", "calc_test.go", "helpers_test.go"], cwd=os.path.join(self.root, "go"),
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_kept_titles_stay_and_deleted_titles_go(self):
        deleted = set(DELETE)
        kept = [t for t in self.inv if t["id"] not in deleted]
        for t in kept:
            self.assertIn(t["title"].encode(), read(self.root, t["file"]), t["id"])
        cart = read(self.root, "ts/cart.test.ts")
        self.assertEqual(cart.count(b'it("adds an item"'), 1)
        self.assertIn(b"cart.add(\"pear\")", cart)  # the kept duplicate is the second one
        for title in (b"adds %i units", b"supports gift cards", b"is the only test here"):
            self.assertNotIn(title, cart)
        go = read(self.root, "go/calc_test.go")
        for title in ("empty", "letters ü", "TestAdd", "is a table test"):
            self.assertNotIn(title.encode(), go)

    def test_empty_containers_are_removed(self):
        self.assertNotIn(b'describe("Empty after delete"', read(self.root, "ts/cart.test.ts"))
        self.assertNotIn(b"nested layer", read(self.root, "ts/session.test.ts"))
        py = read(self.root, "py/test_ledger.py")
        self.assertNotIn(b"class TestWithdraw", py)
        self.assertNotIn(b"class LedgerCase", py)
        self.assertIn(b"class TestSqliteStorage(StorageContract)", py)  # still has a test
        rs = read(self.root, "rs/src/lib.rs")
        self.assertNotIn(b"mod nested", rs)
        self.assertNotIn(b"should_panic", rs)
        self.assertNotIn(b"#[rstest]", rs)
        self.assertNotIn(b"/// Rejects", rs)
        self.assertIn(b"#[cfg(test)]\nmod tests {", rs)
        self.assertNotIn(b't.Run("invalid"', read(self.root, "go/calc_test.go"))  # emptied subtest group goes too

    def test_container_with_a_dropped_test_is_kept(self):
        ts = read(self.root, "ts/mocked.test.ts")
        self.assertIn(b'describe("mocked fs"', ts)
        self.assertIn(b'it("is dropped"', ts)
        self.assertNotIn(b"sees the mock", ts)

    def test_class_with_shared_base_keeps_a_pass_body(self):
        py = read(self.root, "py/test_ledger.py").decode()
        # the comment attached to the deleted test goes with it
        self.assertIn("class TestPostgresStorage(StorageContract):\n    pass\n", py)

    def test_blank_lines_are_tidied(self):
        py = read(self.root, "py/test_ledger.py").decode()
        self.assertIn("    assert ledger.balance == 0\n\n\nasync def test_async_sync", py)
        self.assertNotIn("\n\n\n\n", py)
        cart = read(self.root, "ts/cart.test.ts").decode()
        self.assertIn('describe("add", () => {\n    it("adds an item", () => {\n      cart.add("pear");', cart)
        self.assertTrue(cart.endswith("  if (process.env.SLOW) it(\"only when slow\", () => {});\n});\n"), cart[-80:])

    def test_crlf_is_preserved(self):
        for rel in ("ts/crlf.test.ts", "py/test_crlf.py"):
            data = read(self.root, rel)
            self.assertEqual(data.count(b"\n"), data.count(b"\r\n"), rel)
        self.assertEqual(read(self.root, "ts/crlf.test.ts"),
                         b'import { describe, expect, it } from "vitest";\r\n\r\ndescribe("crlf", () => {\r\n'
                         b'  it("first", () => {\r\n    expect(1).toBe(1);\r\n  });\r\n});\r\n')

    def test_go_file_with_helpers_is_kept(self):
        go = read(self.root, "go/helpers_test.go")
        self.assertIn(b"func mustParse", go)
        self.assertNotIn(b"TestMustParse", go)


class ApplyEdgeCasesTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="test-snap-apply-")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def inventory(self):
        result, _ = inventory.extract(self.root, inventory.find_files(self.root))
        return [t for rel in sorted(result) for t in result[rel][0]]

    def test_reverts_a_file_that_stops_parsing(self):
        self.write("a.test.ts", 'it("a", () => {});\n\nit("b", () => {});\n')
        inv = self.inventory()
        with mock.patch.object(apply, "cut", lambda data, s, e, repl=b"": data[:s] + b"{{" + data[e:]):
            out = apply.apply(inv, [{"id": inv[0]["id"], "verdict": "delete"}], self.root, run_cleanup=False)
        self.assertEqual(out["reverted"], [("a.test.ts", "parse error after edit")])
        self.assertEqual(out["tests_deleted"], 0)
        self.assertEqual(read(self.root, "a.test.ts"), b'it("a", () => {});\n\nit("b", () => {});\n')

    def test_reverts_a_file_a_cleanup_tool_breaks(self):
        self.write("test_x.py", "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n")
        inv = self.inventory()

        def broken_cleanup(repo, edited, ruff_dirty):
            for rel in edited:
                with open(os.path.join(repo, rel), "a", encoding="utf-8") as f:
                    f.write("def (\n")
            return ["fake cleanup ran"]

        with mock.patch.object(apply, "cleanup", broken_cleanup):
            out = apply.apply(inv, [{"id": "test_x.py::test_a#0", "verdict": "delete"}], self.root)
        self.assertEqual(out["reverted"], [("test_x.py", "parse error after cleanup")])
        self.assertEqual(read(self.root, "test_x.py"), b"def test_a():\n    pass\n\n\ndef test_b():\n    pass\n")

    def test_review_verdict_applies_only_when_asked(self):
        self.write("test_x.py", "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n")
        inv = self.inventory()
        dec = [{"id": "test_x.py::test_a#0", "verdict": "review"}]
        self.assertEqual(apply.apply(inv, dec, self.root, run_cleanup=False)["tests_deleted"], 0)
        out = apply.apply(inv, dec, self.root, verdicts=("delete", "review"), run_cleanup=False)
        self.assertEqual(out["tests_deleted"], 1)
        self.assertEqual(read(self.root, "test_x.py"), b"def test_b():\n    pass\n")

    def test_stale_ids_are_reported_not_applied(self):
        self.write("test_x.py", "def test_a():\n    pass\n")
        inv = self.inventory()
        self.write("test_x.py", "def test_renamed():\n    pass\n")
        out = apply.apply(inv, [{"id": "test_x.py::test_a#0", "verdict": "delete"}], self.root, run_cleanup=False)
        self.assertEqual(out["missing"], ["test_x.py::test_a#0"])
        self.assertEqual(read(self.root, "test_x.py"), b"def test_renamed():\n    pass\n")

    def test_attached_comments_go_with_the_test(self):
        self.write("a.test.ts", '// header stays\n\nit("a", () => {});\n\n// about b\n// @ts-expect-error\nit("b", () => {});\n')
        inv = self.inventory()
        apply.apply(inv, [{"id": "a.test.ts::b#0", "verdict": "delete"}], self.root, run_cleanup=False)
        self.assertEqual(read(self.root, "a.test.ts"), b'// header stays\n\nit("a", () => {});\n')

    def test_python_class_used_as_a_base_and_module_helpers_are_kept(self):
        self.write("test_base.py", "def make():\n    return 1\n\n\nclass TestBase:\n    def test_a(self):\n        pass\n\n\n"
                                   "class TestChild(TestBase):\n    def test_b(self):\n        pass\n")
        inv = self.inventory()
        out = apply.apply(inv, [{"id": t["id"], "verdict": "delete"} for t in inv], self.root, run_cleanup=False)
        self.assertEqual((out["deleted"], out["reverted"]), ([], []))
        self.assertEqual(read(self.root, "test_base.py"),
                         b"def make():\n    return 1\n\n\nclass TestBase:\n    pass\n\n\nclass TestChild(TestBase):\n    pass\n")

    @unittest.skipUnless(shutil.which("go"), "go not installed")
    def test_go_locals_only_a_deleted_subtest_used_become_blank(self):
        # a Go repo: `c, srv := newClient(t)` and `want := 3` left unused reverted whole files
        self.write("go.mod", "module example.com/unused\n\ngo 1.21\n")
        self.write("shared_test.go", "package unused\n\nimport \"testing\"\n\nfunc TestShared(t *testing.T) {\n\twant := 3\n"
                                     "\tt.Run(\"uses want\", func(t *testing.T) { t.Log(want) })\n"
                                     "\tt.Run(\"plain\", func(t *testing.T) {})\n}\n")
        self.write("pair_test.go", "package unused\n\nimport \"testing\"\n\nfunc pair() (int, int) { return 1, 2 }\n\n"
                                   "func TestPair(t *testing.T) {\n\ta, b := pair()\n"
                                   "\tt.Run(\"uses a\", func(t *testing.T) { t.Log(a) })\n"
                                   "\tt.Run(\"uses b\", func(t *testing.T) { t.Log(b) })\n}\n")
        inv = self.inventory()
        dec = [{"id": "shared_test.go::TestShared > uses want#0", "verdict": "delete"},
               {"id": "pair_test.go::TestPair > uses b#0", "verdict": "delete"}]
        out = apply.apply(inv, dec, self.root, run_cleanup=False)
        self.assertEqual((out["reverted"], out["tests_deleted"]), ([], 2))
        self.assertIn("go vet: 0 new errors", out["lines"])
        self.assertIn(b"\t_ = 3\n", read(self.root, "shared_test.go"))
        self.assertIn(b"\ta, _ := pair()\n", read(self.root, "pair_test.go"))

    def test_emptied_go_parent_with_code_of_its_own_keeps_that_code(self):
        # a helper check or a t.Run table in the parent is never judged, so it must survive its subtests
        self.write("x_test.go", "package x\n\nimport \"testing\"\n\nfunc check(t *testing.T, ok bool) {\n\tif !ok {\n\t\tt.Fatal()\n\t}\n}\n\n"
                                "func TestHelper(tt *testing.T) {\n\tcheck(tt, true)\n\ttt.Run(\"a\", func(t *testing.T) {})\n}\n\n"
                                "func TestPure(t *testing.T) {\n\t// note\n\tt.Run(\"b\", func(t *testing.T) {\n"
                                "\t\tt.Run(\"c\", func(t *testing.T) {})\n\t})\n}\n")
        inv = self.inventory()
        self.assertEqual([t["id"] for t in inv], ["x_test.go::TestHelper > a#0", "x_test.go::TestPure > b > c#0"])
        out = apply.apply(inv, [{"id": t["id"], "verdict": "delete"} for t in inv], self.root, run_cleanup=False)
        self.assertEqual(read(self.root, "x_test.go"),
                         b"package x\n\nimport \"testing\"\n\nfunc check(t *testing.T, ok bool) {\n\tif !ok {\n\t\tt.Fatal()\n\t}\n}\n\n"
                         b"func TestHelper(tt *testing.T) {\n\tcheck(tt, true)\n}\n")
        self.assertEqual(out["tests_deleted"], 2)
        self.assertIn("  kept x_test.go::TestHelper", out["lines"])

    @unittest.skipUnless(shutil.which("go"), "go not installed")
    def test_go_vet_error_reverts_the_file(self):
        self.write("go.mod", "module example.com/called\n\ngo 1.21\n")
        original = ("package called\n\nimport \"testing\"\n\nfunc TestA(t *testing.T) {\n\tTestB(t)\n}\n\n"
                    "func TestB(t *testing.T) {}\n")
        self.write("called_test.go", original)
        inv = self.inventory()
        out = apply.apply(inv, [{"id": "called_test.go::TestB#0", "verdict": "delete"}], self.root, run_cleanup=False)
        self.assertEqual(out["reverted"], [("called_test.go", "go vet error after edit")])
        self.assertEqual(out["tests_deleted"], 0)
        self.assertIn("go vet: 0 new errors", out["lines"])
        self.assertEqual(read(self.root, "called_test.go"), original.encode())

    @unittest.skipUnless(shutil.which("ruff"), "ruff not installed")
    def test_import_block_stays_sorted_when_the_repo_sorts_imports(self):
        self.write("pyproject.toml", '[tool.ruff.lint]\nselect = ["F", "I"]\n')
        self.write("tests/test_x.py", "import os\n\nimport requests\n\nfrom mypkg import thing\n\n\n"
                                      "def test_a():\n    assert thing and os\n\n\ndef test_b():\n    assert requests\n")
        inv = self.inventory()
        apply.apply(inv, [{"id": "tests/test_x.py::test_b#0", "verdict": "delete"}], self.root)
        r = subprocess.run(["ruff", "check", "--no-cache", "tests"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    @unittest.skipUnless(shutil.which("ruff"), "ruff not installed")
    def test_imports_are_not_sorted_when_the_repo_does_not_sort_them(self):
        self.write("pyproject.toml", '[tool.ruff.lint]\nselect = ["F"]\n')
        self.write("tests/test_x.py", "import sys\nimport os\n\n\ndef test_a():\n    assert os and sys\n\n\n"
                                      "def test_b():\n    pass\n")
        inv = self.inventory()
        apply.apply(inv, [{"id": "tests/test_x.py::test_b#0", "verdict": "delete"}], self.root)
        self.assertTrue(read(self.root, "tests/test_x.py").startswith(b"import sys\nimport os\n"))

    @unittest.skipUnless(shutil.which("cargo"), "cargo not installed")
    def test_rust_imports_only_deleted_tests_used_are_removed(self):
        # archgraph: deleted tests left `use` items that fail `cargo clippy -D warnings`
        self.write("Cargo.toml", '[package]\nname = "snapfix"\nversion = "0.1.0"\nedition = "2021"\n')
        self.write("src/lib.rs", "pub fn a() -> u8 {\n    1\n}\n\npub fn b() -> u8 {\n    2\n}\n\n#[cfg(test)]\n"
                                 "mod tests {\n    use super::{a, b};\n\n    #[test]\n    fn ta() {\n        assert_eq!(a(), 1);\n"
                                 "    }\n\n    #[test]\n    fn tb() {\n        assert_eq!(b(), 2);\n    }\n}\n")
        self.write("Cargo.lock", "# stale lock: unlocked cargo commands would rewrite it\nversion = 3\n")
        inv = self.inventory()
        out = apply.apply(inv, [{"id": "src/lib.rs::tests > tb#0", "verdict": "delete"}], self.root, check=True)
        self.assertEqual(read(self.root, "Cargo.lock"), b"# stale lock: unlocked cargo commands would rewrite it\nversion = 3\n")
        self.assertIn("rustc unused_imports: fixed 1 in 1 files", out["lines"])
        self.assertIn(b"    use super::a;\n", read(self.root, "src/lib.rs"))
        self.assertEqual(out["reverted"], [])

    def test_ts_file_that_exports_helpers_is_kept(self):
        self.write("a.test.ts", 'export const make = () => 1;\n\nit("a", () => {});\n')
        inv = self.inventory()
        out = apply.apply(inv, [{"id": inv[0]["id"], "verdict": "delete"}], self.root, run_cleanup=False)
        self.assertEqual(out["deleted"], [])
        self.assertEqual(read(self.root, "a.test.ts"), b"export const make = () => 1;\n")


if __name__ == "__main__":
    unittest.main()

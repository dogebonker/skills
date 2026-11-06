import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import inventory  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")

# (id, start_line, end_line) for every test unit in the fixtures, in file then source order.
EXPECTED = [
    ("go/calc_test.go::TestAdd#0", 8, 25),
    ("go/calc_test.go::TestParse > valid#0", 28, 32),
    ("go/calc_test.go::TestParse > invalid > empty#0", 35, 39),
    ("go/calc_test.go::TestParse > invalid > letters ü#0", 41, 46),
    ("go/helpers_test.go::TestMustParse#0", 14, 18),
    ("go/only_test.go::TestOnly#0", 5, 10),
    ("go/unused/shared_test.go::TestShared > uses want#0", 8, 12),
    ("py/test_crlf.py::test_one#0", 4, 5),
    ("py/test_crlf.py::test_two#0", 8, 9),
    ("py/test_ledger.py::test_starts_at_zero#0", 13, 14),
    ("py/test_ledger.py::test_deposit#0", 17, 23),
    ("py/test_ledger.py::test_async_sync#0", 26, 27),
    ("py/test_ledger.py::test_café_names_are_utf8#0", 30, 31),
    ("py/test_ledger.py::TestWithdraw > test_withdraw#0", 43, 45),
    ("py/test_ledger.py::TestWithdraw > test_withdraw_too_much#0", 47, 50),
    ("py/test_ledger.py::TestWithdraw > TestNested > test_inner#0", 53, 54),
    ("py/test_ledger.py::LedgerCase > test_repr#0", 61, 62),
    ("py/test_ledger.py::TestSqliteStorage > test_sqlite_only#0", 68, 69),
    ("py/test_ledger.py::TestPostgresStorage > test_pg_only#0", 74, 75),
    ("rs/src/lib.rs::tests > parses_seconds#0", 12, 15),
    ("rs/src/lib.rs::tests > rejects_missing_unit#0", 17, 22),
    ("rs/src/lib.rs::tests > parses_async#0", 24, 27),
    ("rs/src/lib.rs::tests > parses_cases#0", 29, 34),
    ("rs/src/lib.rs::tests > nested > inner#0", 41, 44),
    ("rs/tests/integration.rs::parses_from_setup#0", 7, 10),
    ("rs/tests/integration.rs::parses_zero#0", 12, 15),
    ("ts/Button.browser.test.tsx::Button > renders the label#0", 6, 9),
    ("ts/Button.browser.test.tsx::Button > calls onClick#0", 11, 16),
    ("ts/cart.test.ts::Cart > starts empty#0", 11, 13),
    ("ts/cart.test.ts::Cart > add > adds an item#0", 16, 19),
    ("ts/cart.test.ts::Cart > add > adds an item#1", 21, 24),
    ("ts/cart.test.ts::Cart > add > adds %i units#0", 26, 29),
    ("ts/cart.test.ts::Cart > totals in %s > formats ${currency}#0", 33, 35),
    ("ts/cart.test.ts::Cart > applies a coupon#0", 38, 38),
    ("ts/cart.test.ts::Cart > supports gift cards#0", 39, 39),
    ("ts/cart.test.ts::Cart > adds $a + $b#0", 41, 46),
    ("ts/cart.test.ts::Cart > préfère les accents 日本語#0", 48, 50),
    ("ts/cart.test.ts::Empty after delete > is the only test here#0", 56, 58),
    ("ts/crlf.test.ts::crlf > first#0", 4, 6),
    ("ts/crlf.test.ts::crlf > second#0", 8, 10),
    ("ts/mocked.test.ts::mocked fs > sees the mock#0", 10, 12),  # "is dropped" overlaps a parse error
    ("ts/session.test.ts::expires after ttl#0", 5, 11),
    ("ts/session.test.ts::releases on scope close#0", 13, 13),
    ("ts/session.test.ts::uses the live clock#0", 15, 15),
    ("ts/session.test.ts::roundtrips ids#0", 17, 17),
    ("ts/session.test.ts::with session layer > reads the user#0", 20, 20),
    ("ts/session.test.ts::with session layer > nested layer > still works#0", 23, 23),
    ("ts/session.test.ts::unnamed layer test#0", 28, 28),
]

# What each unit's byte range must start and end with.
RANGE_EDGES = {
    "go/calc_test.go::TestAdd#0": (b"// TestAdd is", b"}"),
    "go/calc_test.go::TestParse > invalid > letters ü#0": (b't.Run("letters', b"})"),
    "py/test_ledger.py::test_deposit#0": (b"@pytest.mark.parametrize(", b"== expected"),
    "py/test_ledger.py::TestWithdraw > test_withdraw_too_much#0": (b"@pytest.mark.slow", b"withdraw(11)"),
    "py/test_ledger.py::test_café_names_are_utf8#0": ("def test_café".encode(), b'caf\\xc3\\xa9"'),
    "rs/src/lib.rs::tests > rejects_missing_unit#0": (b"/// Rejects", b"}"),
    "rs/src/lib.rs::tests > parses_cases#0": (b"#[rstest]", b"}"),
    "rs/src/lib.rs::tests > parses_async#0": (b"#[tokio::test(", b"}"),
    "ts/cart.test.ts::Cart > add > adds %i units#0": (b"it.each([1, 2, 3])", b"});"),
    "ts/cart.test.ts::Cart > adds $a + $b#0": (b"test.each`", b"});"),
    "ts/cart.test.ts::Cart > préfère les accents 日本語#0": ('it("préfère les accents 日本語"'.encode(), b"});"),
    "ts/crlf.test.ts::crlf > second#0": (b'it("second"', b"});"),
    "ts/session.test.ts::expires after ttl#0": (b'it.effect("expires', b");"),
}


class InventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = inventory.find_files(FIXTURES)
        cls.result, cls.warnings = inventory.extract(FIXTURES, cls.files)
        cls.tests = {t["id"]: t for rel in sorted(cls.result) for t in cls.result[rel][0]}

    def test_finds_test_files_by_language(self):
        self.assertEqual(self.files["ts/Button.browser.test.tsx"], "ts")
        self.assertEqual(self.files["py/test_ledger.py"], "py")
        self.assertEqual(self.files["rs/src/lib.rs"], "rs")
        self.assertEqual(self.files["go/calc_test.go"], "go")
        self.assertNotIn("go/calc.go", self.files)
        self.assertNotIn("go/go.mod", self.files)

    def test_exact_ids_and_lines(self):
        got = [(t["id"], t["start_line"], t["end_line"]) for t in self.tests.values()]
        self.assertEqual(got, EXPECTED)

    def test_byte_ranges_cover_the_whole_statement(self):
        for tid, (head, tail) in RANGE_EDGES.items():
            t = self.tests[tid]
            with open(os.path.join(FIXTURES, t["file"]), "rb") as f:
                chunk = f.read()[t["start_byte"]:t["end_byte"]]
            self.assertTrue(chunk.startswith(head), (tid, chunk[:40]))
            self.assertTrue(chunk.endswith(tail), (tid, chunk[-40:]))

    def test_record_shape(self):
        t = self.tests["ts/cart.test.ts::Cart > add > adds an item#1"]
        self.assertEqual(t["path"], ["Cart", "add", "adds an item"])
        self.assertEqual((t["title"], t["occurrence"], t["lang"], t["kind"]), ("adds an item", 1, "ts", "test"))
        self.assertEqual(set(t), {"id", "file", "lang", "title", "path", "occurrence", "start_byte", "end_byte",
                                  "start_line", "end_line", "kind"})

    def test_not_tests(self):
        titles = {t["title"] for t in self.tests.values()}
        for name in ("only when slow", "test_nested_is_ignored", "test_not_collected", "helper", "TestMain",
                     "BenchmarkAdd", "beforeEach", "test_client", "helper_with_doc"):
            self.assertNotIn(name, titles)

    def test_parse_failures_are_skipped_with_warning(self):
        self.assertFalse(any(t["file"].startswith(("ts/broken", "py/test_broken", "go/broken")) for t in self.tests.values()))
        text = "\n".join(self.warnings)
        for rel in ("ts/broken.test.ts", "py/test_broken.py", "go/broken/broken_test.go"):
            self.assertIn(rel, text)
        self.assertIn("ts/mocked.test.ts: 3 parse errors, dropped 1 of 2 tests", text)

    def test_paths_glob_filter(self):
        files = inventory.find_files(FIXTURES, ["py/*"])
        self.assertEqual(set(files), {"py/test_crlf.py", "py/test_ledger.py", "py/test_broken.py"})

if __name__ == "__main__":
    unittest.main()

import unittest

import pytest

from ledger import Ledger, StorageContract


@pytest.fixture
def ledger():
    return Ledger()


def test_starts_at_zero(ledger):
    assert ledger.balance == 0


@pytest.mark.parametrize(
    "amount, expected",
    [(1, 1), (5, 5)],
)
def test_deposit(ledger, amount, expected):
    ledger.deposit(amount)
    assert ledger.balance == expected


async def test_async_sync(ledger):
    await ledger.sync()


def test_café_names_are_utf8():
    assert "café".encode() == b"caf\xc3\xa9"


def helper_not_a_test():
    def test_nested_is_ignored():
        pass


class TestWithdraw:
    def setup_method(self):
        self.ledger = Ledger(balance=10)

    def test_withdraw(self):
        self.ledger.withdraw(3)
        assert self.ledger.balance == 7

    @pytest.mark.slow
    def test_withdraw_too_much(self):
        with pytest.raises(ValueError):
            self.ledger.withdraw(11)

    class TestNested:
        def test_inner(self):
            assert True


class LedgerCase(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()

    def test_repr(self):
        self.assertIn("Ledger", repr(self.ledger))


class TestSqliteStorage(StorageContract):
    backend = "sqlite"

    def test_sqlite_only(self):
        assert self.backend == "sqlite"


class TestPostgresStorage(StorageContract):
    # inherits the contract tests; this one is its own
    def test_pg_only(self):
        assert True


class Helper:
    def test_not_collected(self):
        pass


@pytest.fixture
def test_client():
    return object()

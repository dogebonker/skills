"""Adapter: wrap a third-party client so it fits the interface our code expects."""
from __future__ import annotations

from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, cents: int, currency: str) -> str: ...


class LegacyBank:
    """Third-party API we cannot change: dollars as float, positional args."""

    def make_payment(self, amount: float, cur: str, *, memo: str = "") -> int:
        return 4242


class LegacyBankAdapter:
    def __init__(self, bank: LegacyBank) -> None:
        self._bank = bank

    def charge(self, cents: int, currency: str) -> str:
        ref = self._bank.make_payment(cents / 100, currency.upper())
        return f"txn-{ref}"


def checkout(gateway: PaymentGateway) -> str:
    return gateway.charge(1999, "eur")


if __name__ == "__main__":
    print(checkout(LegacyBankAdapter(LegacyBank())))

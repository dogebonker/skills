"""LSP: a subtype must keep the promises callers rely on. Checking accounts pay the same in both."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


# --- Violation: FixedDepositAccountV1 is an AccountV1 but raises where AccountV1 promised to withdraw.
class AccountV1:
    def __init__(self, balance_cents: int) -> None:
        self.balance_cents = balance_cents

    def withdraw(self, cents: int) -> None:
        if cents > self.balance_cents:
            raise ValueError("insufficient funds")
        self.balance_cents -= cents


class FixedDepositAccountV1(AccountV1):
    def withdraw(self, cents: int) -> None:
        raise PermissionError("fixed deposit: withdrawals locked")


def pay_invoice_v1(source: AccountV1, cents: int) -> str:
    source.withdraw(cents)
    return f"paid {cents}, left {source.balance_cents}"


# --- Fix: split the capability. Only types that can keep the withdraw contract have it.
@runtime_checkable
class Withdrawable(Protocol):
    @property
    def balance_cents(self) -> int: ...

    def withdraw(self, cents: int) -> None: ...


class CheckingAccount:
    def __init__(self, balance_cents: int) -> None:
        self._balance_cents = balance_cents

    @property
    def balance_cents(self) -> int:
        return self._balance_cents

    def withdraw(self, cents: int) -> None:
        if cents > self._balance_cents:
            raise ValueError("insufficient funds")
        self._balance_cents -= cents


class FixedDeposit:
    def __init__(self, balance_cents: int) -> None:
        self._balance_cents = balance_cents

    @property
    def balance_cents(self) -> int:
        return self._balance_cents


def pay_from(source: Withdrawable, cents: int) -> str:
    # mypy rejects pay_from(FixedDeposit(...)): it has no withdraw, so it is not Withdrawable.
    source.withdraw(cents)
    return f"paid {cents}, left {source.balance_cents}"


if __name__ == "__main__":
    print("violation, checking:", pay_invoice_v1(AccountV1(50000), 1000))
    print("fix, checking:      ", pay_from(CheckingAccount(50000), 1000))
    print("same output:", pay_invoice_v1(AccountV1(50000), 1000) == pay_from(CheckingAccount(50000), 1000))
    try:
        pay_invoice_v1(FixedDepositAccountV1(50000), 1000)
    except PermissionError as e:
        print("violation, fixed deposit raises:", e)
    # runtime_checkable isinstance only checks that the members exist, not their signatures.
    accounts: list[object] = [FixedDeposit(50000), CheckingAccount(20000)]
    payable = [type(a).__name__ for a in accounts if isinstance(a, Withdrawable)]
    print("fix, payable sources:", payable)

"""ISP: a client depends only on the methods it calls. Both versions build the same message."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NoReturn, Protocol


@dataclass(frozen=True)
class Customer:
    id: str
    email: str
    overdue: bool = False


class CustomerRepository(ABC):
    @abstractmethod
    def find_email(self, customer_id: str) -> str | None: ...

    @abstractmethod
    def save(self, customer: Customer) -> None: ...

    @abstractmethod
    def remove(self, customer_id: str) -> None: ...

    @abstractmethod
    def list_overdue(self) -> list[Customer]: ...


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self) -> None:
        self._rows: dict[str, Customer] = {}

    def find_email(self, customer_id: str) -> str | None:
        row = self._rows.get(customer_id)
        return row.email if row else None

    def save(self, customer: Customer) -> None:
        self._rows[customer.id] = customer

    def remove(self, customer_id: str) -> None:
        self._rows.pop(customer_id, None)

    def list_overdue(self) -> list[Customer]:
        return [c for c in self._rows.values() if c.overdue]


# --- Violation: needs one method but demands the whole repository ABC.
def welcome_message_v1(repo: CustomerRepository, customer_id: str) -> str:
    email = repo.find_email(customer_id)
    if email is None:
        raise LookupError(f"no customer {customer_id}")
    return f"Welcome! Receipts go to {email}."


# --- Fix: the consumer declares the slice it uses. Any object with find_email fits implicitly.
class EmailLookup(Protocol):
    def find_email(self, customer_id: str) -> str | None: ...


def welcome_message(repo: EmailLookup, customer_id: str) -> str:
    email = repo.find_email(customer_id)
    if email is None:
        raise LookupError(f"no customer {customer_id}")
    return f"Welcome! Receipts go to {email}."


def _unused() -> NoReturn:
    raise AssertionError("not used by welcome_message")


class FatFake(CustomerRepository):
    """The violation's test double: three stubs nobody calls."""

    def find_email(self, customer_id: str) -> str | None:
        return "test@example.com"

    def save(self, customer: Customer) -> None:
        _unused()

    def remove(self, customer_id: str) -> None:
        _unused()

    def list_overdue(self) -> list[Customer]:
        _unused()


class EmailFake:
    """The fix's test double: one method, no base class."""

    def find_email(self, customer_id: str) -> str | None:
        return "test@example.com"


if __name__ == "__main__":
    repo = InMemoryCustomerRepository()
    repo.save(Customer("c-7", "ana@example.com"))
    print("violation:", welcome_message_v1(repo, "c-7"))
    print("fix:      ", welcome_message(repo, "c-7"))
    print("same output:", welcome_message_v1(repo, "c-7") == welcome_message(repo, "c-7"))
    print("violation fake:", welcome_message_v1(FatFake(), "x"))
    print("fix fake:      ", welcome_message(EmailFake(), "x"))

"""Abstract Factory: one factory object yields a matching family of products."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Connection(Protocol):
    def dsn(self) -> str: ...


class Dialect(Protocol):
    def quote(self, name: str) -> str: ...


class DbFactory(Protocol):
    def connection(self) -> Connection: ...
    def dialect(self) -> Dialect: ...


@dataclass
class PgConnection:
    def dsn(self) -> str:
        return "postgres://localhost/app"


@dataclass
class PgDialect:
    def quote(self, name: str) -> str:
        return f'"{name}"'


@dataclass
class MySqlConnection:
    def dsn(self) -> str:
        return "mysql://localhost/app"


@dataclass
class MySqlDialect:
    def quote(self, name: str) -> str:
        return f"`{name}`"


class PgFactory:
    def connection(self) -> Connection:
        return PgConnection()

    def dialect(self) -> Dialect:
        return PgDialect()


class MySqlFactory:
    def connection(self) -> Connection:
        return MySqlConnection()

    def dialect(self) -> Dialect:
        return MySqlDialect()


def select_orders(factory: DbFactory) -> str:
    """Client code sees only the abstract family."""
    d = factory.dialect()
    return f"{factory.connection().dsn()} -> SELECT * FROM {d.quote('orders')}"


if __name__ == "__main__":
    for f in (PgFactory(), MySqlFactory()):
        print(select_orders(f))

"""Decorator (GoF): wrap an object with the same interface to add behavior.

Not the same as Python's @decorator syntax, which wraps a *function*; that
syntax is one way to write the pattern for callables (see `logged` below).
The GoF form below wraps an *object* and composes at runtime.
"""
from __future__ import annotations

import functools
from typing import Callable, Protocol


class DataSource(Protocol):
    def read(self) -> str: ...


class FileSource:
    def read(self) -> str:
        return "hello world"


class Upper:
    def __init__(self, inner: DataSource) -> None:
        self._inner = inner

    def read(self) -> str:
        return self._inner.read().upper()


class Bracketed:
    def __init__(self, inner: DataSource) -> None:
        self._inner = inner

    def read(self) -> str:
        return f"[{self._inner.read()}]"


# Function flavor with @decorator syntax; functools.wraps keeps metadata.
def logged(fn: Callable[[], str]) -> Callable[[], str]:
    @functools.wraps(fn)
    def wrapper() -> str:
        print(f"calling {fn.__name__}")
        return fn()

    return wrapper


@logged
def greet() -> str:
    return "hi"


if __name__ == "__main__":
    print(Bracketed(Upper(FileSource())).read())
    print(Upper(Bracketed(FileSource())).read())
    print(greet(), greet.__name__)

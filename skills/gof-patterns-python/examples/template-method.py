"""Template Method: the base class fixes the skeleton, subclasses fill the steps."""
from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator


class Importer(ABC):
    def run(self, raw: str) -> list[dict[str, str]]:  # the template
        rows = self.parse(raw)
        valid = [r for r in rows if self.is_valid(r)]
        self.after_import(valid)
        return valid

    @abstractmethod
    def parse(self, raw: str) -> list[dict[str, str]]: ...

    def is_valid(self, row: dict[str, str]) -> bool:  # hook with default
        return True

    def after_import(self, rows: list[dict[str, str]]) -> None:  # optional hook
        pass


class CsvImporter(Importer):
    def parse(self, raw: str) -> list[dict[str, str]]:
        head, *lines = raw.splitlines()
        cols = head.split(",")
        return [dict(zip(cols, ln.split(","))) for ln in lines]

    def is_valid(self, row: dict[str, str]) -> bool:
        return bool(row.get("email"))


@contextmanager
def import_job(name: str) -> Iterator[None]:
    """Context-manager flavor: fixed setup/teardown around caller's body."""
    print(f"start {name}")
    try:
        yield
    finally:
        print(f"end {name}")


if __name__ == "__main__":
    with import_job("users"):
        print(CsvImporter().run("name,email\nana,a@x.io\nbo,"))

"""Bridge: vary the abstraction (report) and the implementation (sink) independently."""
from __future__ import annotations

from typing import Protocol


class Sink(Protocol):
    def write(self, text: str) -> None: ...


class ConsoleSink:
    def write(self, text: str) -> None:
        print(f"[console] {text}")


class ListSink:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)


class Report:
    def __init__(self, sink: Sink) -> None:  # the bridge
        self.sink = sink

    def publish(self, rows: list[int]) -> None:
        raise NotImplementedError


class TotalReport(Report):
    def publish(self, rows: list[int]) -> None:
        self.sink.write(f"total={sum(rows)}")


class DetailReport(Report):
    def publish(self, rows: list[int]) -> None:
        for i, r in enumerate(rows, 1):
            self.sink.write(f"row {i}: {r}")


if __name__ == "__main__":
    data = [10, 20, 30]
    TotalReport(ConsoleSink()).publish(data)
    store = ListSink()
    DetailReport(store).publish(data)
    print(store.lines)

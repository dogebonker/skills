"""Speculative generality: an abstract base with one subclass, a hook nobody
overrides and parameters nobody passes. The fix keeps only what callers use."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


# --- Violation ---
class BaseNotifier(ABC):
    def before_send(self, message: str) -> str:  # hook: no subclass overrides it
        return message

    @abstractmethod
    def deliver(self, to: str, message: str) -> str: ...

    def send(
        self,
        to: str,
        message: str,
        retries: int = 0,  # every caller passes the default
        transform: Callable[[str], str] | None = None,  # never passed
    ) -> str:
        message = self.before_send(message)
        if transform is not None:
            message = transform(message)
        return self.deliver(to, message)


class EmailNotifier(BaseNotifier):  # the only implementation
    def __init__(self, outbox: list[str]) -> None:
        self.outbox = outbox

    def deliver(self, to: str, message: str) -> str:
        line = f"{to}: {message}"
        self.outbox.append(line)
        return line


# --- Fix ---
def send_email(outbox: list[str], to: str, message: str) -> str:
    line = f"{to}: {message}"
    outbox.append(line)
    return line


if __name__ == "__main__":
    before_box: list[str] = []
    after_box: list[str] = []
    notifier = EmailNotifier(before_box)
    for to in ("ana@example.com", "rui@example.com"):
        notifier.send(to, "Welcome to the shop")
        send_email(after_box, to, "Welcome to the shop")
    print(after_box, "same" if before_box == after_box else "DIFFERENT")

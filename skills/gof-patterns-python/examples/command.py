"""Command: requests as objects, with undo. Plain callables work for simple cases."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class Cart:
    items: list[str]


@dataclass
class AddItem:
    cart: Cart
    item: str
    _index: int = field(default=-1, init=False)

    def execute(self) -> None:
        # Remember the position, so undo removes this item and not an equal one earlier in the list
        self._index = len(self.cart.items)
        self.cart.items.append(self.item)

    def undo(self) -> None:
        del self.cart.items[self._index]


class History:
    def __init__(self) -> None:
        self._done: list[Command] = []

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self._done.append(cmd)

    def undo(self) -> None:
        if self._done:
            self._done.pop().undo()


if __name__ == "__main__":
    cart, history = Cart([]), History()
    history.run(AddItem(cart, "book"))
    history.run(AddItem(cart, "pen"))
    print(cart.items)
    history.undo()
    print(cart.items)
    # No undo needed? A callable is already a command.
    queue: list[Callable[[], None]] = [lambda: print("send email"), lambda: print("log")]
    for job in queue:
        job()

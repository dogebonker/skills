"""Memento: frozen dataclass snapshots of an editor's state."""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Snapshot:
    text: str
    cursor: int


@dataclass
class Editor:
    text: str = ""
    cursor: int = 0

    def type(self, s: str) -> None:
        self.text = self.text[: self.cursor] + s + self.text[self.cursor :]
        self.cursor += len(s)

    def save(self) -> Snapshot:
        return Snapshot(self.text, self.cursor)

    def restore(self, snap: Snapshot) -> None:
        self.text, self.cursor = snap.text, snap.cursor


if __name__ == "__main__":
    ed, undo_stack = Editor(), []
    for word in ("hello", " world"):
        undo_stack.append(ed.save())
        ed.type(word)
    print(repr(ed.text))
    ed.restore(undo_stack.pop())
    print(repr(ed.text))
    snap = ed.save()
    print(replace(snap, cursor=0))  # snapshots are immutable; derive new ones

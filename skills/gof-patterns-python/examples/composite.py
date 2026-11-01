"""Composite: files and folders answer size() through one interface."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class Node(Protocol):
    name: str

    def size(self) -> int: ...


@dataclass
class File:
    name: str
    bytes_: int

    def size(self) -> int:
        return self.bytes_


@dataclass
class Folder:
    name: str
    children: list[Node] = field(default_factory=list)

    def add(self, node: Node) -> Folder:
        self.children.append(node)
        return self

    def size(self) -> int:
        return sum(c.size() for c in self.children)


if __name__ == "__main__":
    tree = Folder("root").add(File("a.txt", 100)).add(
        Folder("docs").add(File("b.md", 40)).add(File("c.md", 60))
    )
    print(tree.name, tree.size())

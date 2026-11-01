"""Prototype: clone a configured object, then tweak the copy."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace


@dataclass
class ReportTemplate:
    title: str
    columns: list[str] = field(default_factory=list)
    footer: str = "confidential"


if __name__ == "__main__":
    base = ReportTemplate("Sales", ["region", "total"])

    # Shallow copy with overrides: dataclasses.replace.
    q1 = replace(base, title="Sales Q1")
    print(q1.columns is base.columns)  # True: nested list is shared

    # Independent copy: deepcopy.
    q2 = copy.deepcopy(base)
    q2.title = "Sales Q2"
    q2.columns.append("margin")
    print(base.columns, q2.columns)

    # A registry of prototypes is just a dict.
    registry = {"sales": base}
    clone = copy.deepcopy(registry["sales"])
    assert clone == base and clone is not base
    print(clone)

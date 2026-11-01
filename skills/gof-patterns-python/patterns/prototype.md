# Prototype

Create new objects by copying a configured instance, using `copy`, `copy.deepcopy` or `dataclasses.replace`.

Refs: https://refactoring.guru/design-patterns/prototype/python/example
Example: [examples/prototype.py](../examples/prototype.py)

**Intent** — Produce new objects from an existing one without coupling to its class or re-running expensive setup.

**Problem** — You need many near-identical objects (report templates, game units) that differ in a few fields.

**Applicability** — **Use** when initialisation is costly or you hold a catalogue of preconfigured instances. **Avoid** a `clone()` method when the standard library already covers it, which it does: you rarely write a `clone()` method in Python.

**Python implementation** — `dataclasses.replace(base, title=...)` makes a shallow copy with overrides; `copy.deepcopy(base)` makes an independent graph. The example demonstrates the key gotcha: after `replace`, `q1.columns is base.columns` is True because the list is shared, so mutate only after `deepcopy` or pass a fresh list. A registry of prototypes is a plain `dict[str, ReportTemplate]`. Customise copying with `__copy__` or `__deepcopy__` only when needed (open file handles, locks).

**Consequences** — No parallel class hierarchy and cheap variants. Cost: aliasing bugs from shallow copies, and deep copies of big graphs can be slow.

**Related patterns** — **Memento** also snapshots state; **Abstract Factory** may be implemented with prototypes; **Flyweight** shares instead of copying.

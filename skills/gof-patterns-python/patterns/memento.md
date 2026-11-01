# Memento

A frozen snapshot of an object's state lets you restore it later without exposing its internals.

Refs: https://refactoring.guru/design-patterns/memento/python/example
Example: [examples/memento.py](../examples/memento.py)

**Intent** — Capture and restore an object's state while respecting encapsulation.

**Problem** — An editor needs undo, but outside code should not poke at its fields.

**Applicability** — **Use** for undo, checkpoints and rollback. **Avoid** a memento class when the state is a small immutable value you can just keep (a tuple), or when `copy.deepcopy(obj)` is acceptable; with immutable state, the "memento" is the state itself.

**Python implementation** — `Snapshot` is a `@dataclass(frozen=True)`, so callers cannot alter it. `Editor.save()` returns one and `restore(snap)` reads it back. The caretaker is the plain `undo_stack` list in the demo, holding snapshots without inspecting them. `dataclasses.replace` derives modified snapshots. Python cannot truly hide fields, so a leading underscore documents intent. Gotcha: mutable members (lists, dicts) inside a frozen dataclass are still shared, so copy them on save.

**Consequences** — Simple undo with strong separation. Cost: memory for many snapshots, so cap the stack or store diffs.

**Related patterns** — **Command** uses mementos to implement undo; **Prototype** is an alternative copy mechanism; **Iterator** can save its position this way.

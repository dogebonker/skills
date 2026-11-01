# Memento

A snapshot value of an object's state that only the owner can read, used to restore it later.

Refs: https://refactoring.guru/design-patterns/memento/swift/example
Example: [examples/memento.swift](../examples/memento.swift)

**Intent** — Capture and restore an object's internal state without breaking encapsulation.

**Problem** — An editor needs undo and must not expose its internals to the history.

**Applicability** — **Use** when you need undo, checkpoints, or rollback and state is not trivially public. **Avoid** a separate memento type when the state is already a plain struct: copying the struct is enough, and `Codable` covers persistent snapshots.

**Swift implementation** — Nest a `Snapshot` struct in the owner with `fileprivate` properties, so outsiders can hold it but not inspect it, and add `snapshot()` and `restore(_:)`, as `TextEditor` does. The caller keeps a `[Snapshot]` stack. Because the editor is a struct, the snapshot is cheap thanks to copy on write. For classes, copy the fields you need explicitly. Make snapshots `Codable` to persist them.

**Consequences** — Safe undo without leaking internals. Large snapshots consume memory, so cap the history.

**Related patterns** — **Command** uses mementos to undo; **Iterator** can capture its position; **Prototype** is a simpler copy-based alternative.

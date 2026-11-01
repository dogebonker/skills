# Memento

An opaque snapshot value with unexported fields, created by the owner and handed back to it for restore.

Refs: https://refactoring.guru/design-patterns/memento/go/example
Example: [examples/memento.go](../examples/memento.go)

**Intent** — Save an object's internal state so it can be restored, without breaking encapsulation.

**Problem** — A grid editor supports undo, but outside code must not read or edit the internal cells.

**Applicability** — **Use** when you need undo, checkpoints or rollback of an object whose fields are private. **Avoid** a memento type when the state is a small value type or inverse operations are cheaper: assignment is the snapshot, or keep a Command history.

**Go implementation** — Define `Snapshot` with an unexported field, add `Save() Snapshot` and `Restore(Snapshot)` on the owner, and keep a slice of snapshots as history. Copy reference data in both directions (see `clone`) so later edits do not leak into saved states. Because fields are unexported, other packages can hold a snapshot but cannot inspect it. For plain value structs, `saved := state` is already a memento.

**Consequences** — Safe undo without breaking encapsulation. The cost is memory per snapshot and a deep copy on every save.

**Related patterns** — **Command** undoes via inverse operations instead of snapshots; **Prototype** also copies state, for creation; **Iterator** for capturing a traversal position.

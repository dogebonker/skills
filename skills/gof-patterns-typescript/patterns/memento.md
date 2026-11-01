# Memento

The owner of the state creates an opaque, frozen snapshot, and another object stores it and later hands it back to restore.

Refs: https://refactoring.guru/design-patterns/memento/typescript/example
Example: [examples/memento.ts](../examples/memento.ts)

**Intent** — Capture and restore an object's state without breaking encapsulation.

**Problem** — A form needs undo or draft restore, but exposing its fields just to save them would break its invariants.

**Applicability** — **Use** when you need checkpoints, undo, or rollback while the internals stay private. **Avoid** a memento class when state held as plain immutable data (a reducer with previous states) makes undo a list of values.

**TypeScript implementation** — `FormEditor.save()` returns a frozen copy typed as the branded `Snapshot`, a `unique symbol` brand that outsiders cannot read or forge by accident. Only `restore` casts it back. The history array lives with the caller. Copy on save and on restore so later edits cannot alter stored snapshots. Gotcha: `structuredClone` is better than spread for nested state.

**Consequences** — Undo without exposing internals. Snapshots cost memory in proportion to state size and history length.

**Related patterns** — **Command** records operations instead of states; **Prototype** can produce the copy; **Iterator** steps through the saved history.

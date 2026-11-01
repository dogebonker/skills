# Memento

A snapshot type with private fields in the owner's module, returned by `save` and consumed by `restore`.

Refs: https://refactoring.guru/design-patterns/memento/rust/example
Example: [examples/memento.rs](../examples/memento.rs)

**Intent** — Save a value's internal state so it can be restored later, without exposing the internals.

**Problem** — An editor needs checkpoints, but callers must not read or edit the saved state.

**Applicability** — **Use** when you need undo, rollback or checkpoints of private state. **Avoid** a memento type when the state is `Clone` with public fields: keeping a clone is enough. Use a memento when privacy matters.

**Rust implementation** — Put `Editor` and `Snapshot` in `mod editor`. `Snapshot`'s fields are private to the module, so outside code can hold it but not inspect it. `save(&self) -> Snapshot` clones state, and `restore(&mut self, snap: Snapshot)` takes it by value, so a checkpoint is used once. A `Vec<Snapshot>` is the history. The gotcha: Rust privacy is module-based, not type-based, so the owner and memento must share a module. Cloning large state is costly, so store diffs or use persistent data structures if needed.

**Consequences** — Encapsulated undo. The cost is memory per snapshot.

**Related patterns** — **Command** stores operations to undo, not state; **Prototype** for copying without privacy concerns; **Iterator** can snapshot its position.

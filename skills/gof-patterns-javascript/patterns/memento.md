# Memento

Captures an object's state as an immutable snapshot that can be restored later without exposing the object's internals.

Refs: https://github.com/HowProgrammingWorks/Memento  
Example: [examples/memento.js](../examples/memento.js)

**Intent** — Save and restore the previous state of an object while preserving encapsulation.

**Problem** — Undo, drafts and rollback need the old state, but outside code must not read or rewrite private fields.

**Applicability** — **Use** for undo stacks, drafts, checkpoints and transactional rollback. **Avoid** snapshots when state is already immutable data: keeping the old reference is enough.

**JS implementation** — The originator (`Document`) keeps state in a `#state` private field, creates snapshots with `structuredClone` plus `Object.freeze` in `save()`, and takes them back in `restore()`, which ignores a missing snapshot so undo on an empty history does nothing. The caretaker (`History`) only stores and returns mementos. `structuredClone` copies plain data only: functions, class instances and DOM nodes are lost or throw, so snapshot serializable fields. Gotcha: clone on both save and restore, otherwise the snapshot shares references with live state.

**Consequences** — Simple undo without breaking encapsulation; large states make snapshots expensive in memory and time.

**Related patterns** — **Command** undoes with inverse operations instead of snapshots; **Prototype** for the cloning step; **Iterator** steps through saved states.

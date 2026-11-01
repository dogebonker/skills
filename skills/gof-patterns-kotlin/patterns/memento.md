# Memento

An immutable data class captures an object's state so it can be restored later without exposing its internals.

Refs: https://refactoring.guru/design-patterns/memento/java/example
Example: [examples/memento.kt](../examples/memento.kt)

**Intent** — Save and restore an object's previous state without breaking encapsulation.

**Problem** — An editor needs undo for text and cursor, but other code must not reach into its fields.

**Applicability** — **Use** when you need snapshots, undo or rollback of an object's state. **Avoid** a separate memento class when state is already an immutable value: keeping the old value (`val old = state`) or a data class `copy()` is enough.

**Kotlin implementation** — `Editor.Snapshot` is a nested data class holding `text` and `cursor`. `save()` creates one and `restore(snapshot)` applies it. Callers keep snapshots in an `ArrayDeque` as an undo stack and never edit them. Make the snapshot constructor `internal` to stop other modules creating snapshots; `private` would also hide it from `Editor`, because an outer class cannot see a nested class's private members. On Android, `onSaveInstanceState(Bundle)` and `SavedStateHandle` save and restore UI state across process death, and `Parcelable` is the serialisation form. Gotcha: snapshots of large state use memory, so cap the history or store diffs.

**Consequences** — Safe undo and rollback. Large or frequent snapshots cost memory.

**Related patterns** — **Command** for undo by reversing an action; **Prototype** for copying state; **Iterator** for saving an iteration position.

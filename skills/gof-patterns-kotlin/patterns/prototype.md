# Prototype

A data class gives you `copy()`, which creates a new object from an existing one with selected fields changed.

Refs: https://refactoring.guru/design-patterns/prototype/java/example
Example: [examples/prototype.kt](../examples/prototype.kt)

**Intent** — Create new objects by copying a configured instance, without depending on its class details.

**Problem** — You have a well-configured profile or template and want many variants. Rebuilding each from scratch repeats settings and couples code to constructors.

**Applicability** — **Use** when objects are expensive or tedious to configure and variants differ in a few fields. **Avoid** `Cloneable` and `clone()` when the type is a data class: `copy()` is enough.

**Kotlin implementation** — Model the object as `data class UserProfile(...)` with `val` properties and call `template.copy(name = "ana")`. `copy()` is shallow. That is safe when nested values are immutable, as `Address` and `List` are in the example. Nested mutable state (a `MutableList`, an array) is shared between copies, so copy it explicitly: `copy(tags = tags.toMutableList())`. For non-data classes, add a method or a secondary constructor that takes the original. Avoid `Cloneable`: it is awkward in Kotlin and Java. The same mechanism powers Memento snapshots.

**Consequences** — Cheap variants and no subclass per configuration. The risk is shared mutable state across copies.

**Related patterns** — **Memento** for a copy kept to restore later; **Factory Method** creates by class, not by copying; **Singleton** has the opposite goal: exactly one instance.

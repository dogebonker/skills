# Prototype

Copying an existing value to make a new one, which Swift does for free with structs and by a `copy()` method for classes.

Refs: https://refactoring.guru/design-patterns/prototype/swift/example
Example: [examples/prototype.swift](../examples/prototype.swift)

**Intent** — Create new objects by cloning a configured instance instead of constructing from scratch.

**Problem** — Building an object from nothing is costly or repetitive, and you want variants of a preset.

**Applicability** — **Use** when you need many variations of a configured preset, or the exact type of the thing to copy is only known through a protocol. **Avoid** a clone protocol when the type is a struct or enum: assignment copies with value semantics, so `var variant = base` is enough (arrays and dictionaries copy on write).

**Swift implementation** — Prefer value types: `var variant = base; variant.name = ...` leaves `base` untouched, as `Template` shows. For classes define a `Cloneable` protocol returning `Self` and implement `copy()` through an initializer, as `Layer` does. Remember that a class property holding another class is shared unless you deep copy it. Avoid `NSCopying` outside Foundation or Objective-C interop.

**Consequences** — Cheap variants and no dependence on concrete types. Deep copying object graphs of classes is easy to get wrong.

**Related patterns** — **Memento** also snapshots state; **Factory Method** is the alternative when copying is not wanted; **Composite** often needs deep clones of its trees.

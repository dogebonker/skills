# Prototype

A `Clone` method that deep-copies the slices and maps, since plain assignment copies slice headers and map references, so both values would share the same backing data.

Refs: https://refactoring.guru/design-patterns/prototype/go/example
Example: [examples/prototype.go](../examples/prototype.go)

**Intent** — Create new objects by copying an existing one, so callers need not know how to rebuild it.

**Problem** — A template invoice has lines and metadata; building each new one from scratch repeats setup, and naive copies share the same slice and map.

**Applicability** — **Use** when copies of a preconfigured value are cheaper or simpler than building new ones, and you must hand out independent copies. **Avoid** a `Clone` method when the struct has only value fields: assignment `b := a` already copies it.

**Go implementation** — Assignment copies value fields for free, so `Clone` only needs to duplicate reference fields: use `slices.Clone` and `maps.Clone`, as `Invoice.Clone` does. Pointers inside the struct are shared unless you copy them too. A generic `Cloner[T]` interface lets code hold a prototype without a concrete type. Gotcha: forgetting one map field creates silent aliasing bugs.

**Consequences** — Cheap, independent copies with no dependency on concrete types. The cost is that every new reference field must be added to `Clone`.

**Related patterns** — **Builder** configures a fresh object instead of copying one; **Memento** also copies state, for restoring rather than duplicating.

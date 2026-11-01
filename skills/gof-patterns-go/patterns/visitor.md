# Visitor

A type switch (or a few functions) over a closed set of types, with a sealed interface.

Refs: https://refactoring.guru/design-patterns/visitor/go/example
Example: [examples/visitor.go](../examples/visitor.go)

**Intent** — Separate operations from the objects they operate on, so adding an operation does not modify the types.

**Problem** — Shapes need area, description and later export, and each new operation should not touch every shape.

**Applicability** — **Use** when the set of types is stable, the set of operations grows, and you need to dispatch on concrete type. **Avoid** accept-visit double dispatch when types change often or no operation needs to be a pluggable object: an interface method or a type switch is enough.

**Go implementation** — Mark the closed set with an unexported method (`isShape`) so outsiders cannot add types, then write each operation as a function with `switch v := s.(type)`, as `area` and `describe` do. Add a `default` that panics or returns an error so a forgotten type surfaces. The classic `Accept`/`Visit` pair is only worth it when operations must be pluggable objects. Gotcha: adding a new type silently skips switches without a default.

**Consequences** — New operations are cheap and live together. The cost is that adding a type means finding every switch.

**Related patterns** — **Iterator** walks the structure being visited; **Composite** is the tree usually visited; **Command** for operations as first-class values.

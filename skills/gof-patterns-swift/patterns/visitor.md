# Visitor

An enum with cases plus functions that `switch` over it, which adds new operations without editing the node types.

Refs: https://refactoring.guru/design-patterns/visitor/swift/example
Example: [examples/visitor.swift](../examples/visitor.swift)

**Intent** — Separate operations from the object structure they work on so you can add operations without changing the structure.

**Problem** — An expression tree needs evaluating, printing, and later more operations.

**Applicability** — **Use** when the set of node kinds is stable but operations keep growing. **Avoid** `accept`/`visit` double dispatch when the node kinds form a closed enum: a `switch` over the enum is enough and checks exhaustiveness.

**Swift implementation** — Define `enum Expr` with `indirect` recursive cases and write `evaluate` and `render` as ordinary functions with an exhaustive `switch`, as the example does. The compiler reports every function that misses a new case. Use a protocol-based visitor (`accept(_:)`) only when the nodes are separate types you cannot switch over, such as a class hierarchy from another module.

**Consequences** — Easy new operations and compile-checked coverage. Adding a case forces edits to every operation.

**Related patterns** — **Composite** is the structure it visits; **Iterator** traverses without operations; **Command** is an operation as an object.

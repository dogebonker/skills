# Visitor

A discriminated union of node types with one function per operation, each an exhaustive `switch` on the tag.

Refs: https://refactoring.guru/design-patterns/visitor/typescript/example
Example: [examples/visitor.ts](../examples/visitor.ts)

**Intent** — Add new operations to a set of types without changing those types.

**Problem** — An expression tree needs evaluating, printing, and later optimising, and adding each as a method pollutes the node classes.

**Applicability** — **Use** when the set of node types is stable, and new operations are added often. **Avoid** accept/visit double dispatch when node types form a closed union: a union and `switch` are enough. Use class-based Visitor only when node types are open classes from a library.

**TypeScript implementation** — `Expr` is a tagged union and `evaluate` and `show` are separate functions that `switch (e.kind)` and recurse. The `default` branch assigns to `never`, so adding a node kind fails to compile until every operation handles it. Gotcha: this inverts the trade-off: new operations are easy, new node types touch every function.

**Consequences** — New operations without touching nodes, and the compiler finds missing cases. Adding node types is expensive.

**Related patterns** — **Composite** for the tree it walks; **Iterator** traverses nodes; **State** uses the same union technique.

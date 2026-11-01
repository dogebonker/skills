# Visitor

A new operation over a fixed family of node types is written outside them, dispatched by type with `functools.singledispatch`.

Refs: https://refactoring.guru/design-patterns/visitor/python/example
Example: [examples/visitor.py](../examples/visitor.py)

**Intent** — Add operations to an object structure without modifying its classes.

**Problem** — Expression nodes need evaluation, printing and more, and you do not want each operation added to every node class.

**Applicability** — **Use** when node types are stable and operations keep growing. **Avoid** accept/visit double dispatch: `singledispatch` selects the implementation by the first argument's type already. For two types of arguments or union matching, `match` statements (3.10) or `isinstance` chains also work.

**Python implementation** — Nodes are plain `@dataclass`es (`Num`, `Add`, `Mul`) with no `accept` method. Each operation (`evaluate`, `render`) is a `@singledispatch` function with a default that raises `TypeError`, and `@evaluate.register` overloads per type, with the type taken from the annotation. Recursion calls the generic function again. `singledispatch` gives no static coverage check; for a closed set of node types prefer `match` with an `assert_never`-style fallback so a type checker flags a missing case. Gotchas: dispatch follows the MRO, so a handler registered for a base class already covers its subclasses, and `register` with annotations needs them resolvable at runtime.

**Consequences** — Operations are grouped by purpose and nodes stay simple. Cost: adding a node type means editing every operation.

**Related patterns** — **Composite** gives the structure being visited; **Iterator** supplies traversal; **Command** is similar in making operations explicit.

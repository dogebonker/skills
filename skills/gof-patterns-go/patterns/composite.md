# Composite

An interface implemented by both leaf types and a container that holds child interface values.

Refs: https://refactoring.guru/design-patterns/composite/go/example
Example: [examples/composite.go](../examples/composite.go)

**Intent** — Compose objects into tree structures and treat single objects and groups uniformly.

**Problem** — A directory holds files and other directories, and callers want a total size or a printout without checking which is which.

**Applicability** — **Use** when data forms a tree and operations such as size, render or validate apply recursively. **Avoid** a component interface when the structure is flat or fixed depth: a slice of values, or one type with a `children` field, is enough.

**Go implementation** — Define `Node` with the operations (`Size`, `Print`), implement it on `file` (leaf) and `*dir` (container), and let `dir` loop over `[]Node` and recurse. Use a pointer receiver for the container so `Add` mutates it, as the example does. Keep the interface small; child-management methods like `Add` live on the container only, not on the shared interface. Gotcha: cycles in the graph cause infinite recursion, so guard if children can be shared.

**Consequences** — Uniform recursive operations and simple clients. The cost is an interface wide enough for all node kinds and weaker type safety about what a container may hold.

**Related patterns** — **Iterator** traverses the tree without recursion in the client; **Visitor** adds operations over the tree without editing nodes; **Decorator** has a similar recursive shape with one child.

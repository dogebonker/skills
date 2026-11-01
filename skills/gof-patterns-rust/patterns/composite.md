# Composite

A recursive enum whose container variant holds `Vec<Node>`, with `match` doing the dispatch.

Refs: https://refactoring.guru/design-patterns/composite/rust/example
Example: [examples/composite.rs](../examples/composite.rs)

**Intent** — Compose objects into trees and let callers treat leaves and branches uniformly.

**Problem** — A file system has files and directories that contain both. Totalling size should not need separate code for each case.

**Applicability** — **Use** when the data is naturally a tree and operations apply recursively. **Avoid** a component trait with leaf and composite structs when the node kinds are a closed set: an enum is enough, and a flat `Vec` when there is no nesting.

**Rust implementation** — `enum Node { File { .. }, Dir { name, children: Vec<Node> } }` is the whole structure. `Vec` already heap-allocates the children, so no `Box` is needed there. A direct recursive field such as `Add(Box<Expr>, Box<Expr>)` does need `Box`, or the type has infinite size. Methods like `size` and `print` use `match self` and recurse. Use `Vec<Box<dyn Component>>` only when third parties add new node kinds. The gotcha: parent pointers need `Weak`, so prefer passing context down during traversal.

**Consequences** — Uniform recursive operations with exhaustive matching. The cost is that adding a new operation touches one `match` each, and adding a variant touches all of them.

**Related patterns** — **Visitor** adds operations over a composite; **Iterator** traverses a composite; **Decorator** also wraps recursively, but one child.

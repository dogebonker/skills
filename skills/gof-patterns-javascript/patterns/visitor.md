# Visitor

Adds new operations over a tree of node types without changing the nodes; in JavaScript an object of handlers keyed by node `type`.

Refs: https://github.com/HowProgrammingWorks/Visitor  
Example: [examples/visitor.js](../examples/visitor.js)

**Intent** — Separate an operation from the structure it works on so new operations can be added without editing the node types.

**Problem** — A tree (AST, document, file system) needs many operations (evaluate, print, validate), and each one should not add a method to every node class.

**Applicability** — **Use** when node types are stable and operations keep growing. **Avoid** `accept(visitor)` double dispatch when nodes can be plain data: tagging nodes with `type` and dispatching by lookup is enough. For a flat list, `map` and `reduce` are enough.

**JS implementation** — Nodes are plain objects with a `type`; each visitor (`evaluate`, `print`) is an object with one function per type, taking `(node, go)` where `go` visits a child. `visit` does the lookup with `Object.hasOwn` and throws on an unknown type. Gotcha: recursion depth follows tree depth, so a very deep tree overflows the stack unless `visit` keeps an explicit stack.

**Consequences** — Operations are added in one place and nodes stay plain data; adding a node type means touching every visitor.

**Related patterns** — **Composite** for the tree being visited; **Iterator** traverses without an operation; **Strategy** for picking one function when no tree is involved.

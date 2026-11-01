# Composite

Leaves and containers implement the same interface, and containers delegate to their children recursively.

Refs: https://refactoring.guru/design-patterns/composite/typescript/example
Example: [examples/composite.ts](../examples/composite.ts)

**Intent** — Treat individual objects and groups of objects uniformly in a tree structure.

**Problem** — A folder holds files and folders, and callers want one `size()` call that works at any level.

**Applicability** — **Use** when the model is a part-whole tree and clients should ignore the difference between a node and a branch. **Avoid** a Composite class hierarchy when the tree has a few fixed shapes: a discriminated union with a recursive function is shorter and checked for exhaustiveness.

**TypeScript implementation** — `FsNode` is the shared interface; `FileNode` returns its size and `FolderNode` sums `children` via `reduce` and `flatMap` for printing. `add(...nodes): this` allows chaining. Put child-management methods on the container only, not the interface, to keep leaves honest. Gotcha: cycles cause infinite recursion, so guard if nodes can be re-parented.

**Consequences** — Client code stays simple and recursion is natural. A very general interface can allow nonsense such as adding a child to a file.

**Related patterns** — **Iterator** walks the tree; **Visitor** adds operations over the tree; **Decorator** has the same recursive shape with one child.

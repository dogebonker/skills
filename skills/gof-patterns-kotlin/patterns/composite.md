# Composite

A sealed interface with leaf and container implementations lets callers treat a single item and a tree of items through one type.

Refs: https://refactoring.guru/design-patterns/composite/java/example
Example: [examples/composite.kt](../examples/composite.kt)

**Intent** — Compose objects into trees and work with them uniformly.

**Problem** — A file manager has files and folders, and callers want the total size of anything without checking which it is.

**Applicability** — **Use** when data forms a part-whole tree and operations should work on a node or a whole subtree. **Avoid** a component hierarchy when the structure is flat or you only need totals: a `List`, or a recursive function over a data class, is enough.

**Kotlin implementation** — `sealed interface Entry` declares `name` and `size()`. `FileEntry` is the leaf, and `Folder` holds `children` and sums them with `sumOf`. A `vararg` secondary constructor makes literals tidy. Shared operations (`size`, `print`) live on `Entry`, so `Folder` just calls them on each child with no type checks; use an exhaustive `when` over the sealed type only for operations defined outside the hierarchy. In Android, `ViewGroup` and `View`, and Compose's nested composables, are composites. Gotcha: keep child management out of the leaf interface so leaves do not carry methods that throw.

**Consequences** — Uniform treatment and simple recursion. A very general interface can allow meaningless trees.

**Related patterns** — **Iterator** walks a composite; **Visitor** adds operations over the tree; **Decorator** is also recursive, but wraps one object.

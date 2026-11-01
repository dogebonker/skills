# Visitor

With a sealed hierarchy, an exhaustive `when` inside an extension function is a visitor, and each new operation is a new function.

Refs: https://refactoring.guru/design-patterns/visitor/java/example
Example: [examples/visitor.kt](../examples/visitor.kt)

**Intent** — Add operations to a family of types without changing those types.

**Problem** — An expression tree needs evaluation, printing and later more operations, and adding each to the node classes would bloat them.

**Applicability** — **Use** when a stable set of node types needs many operations that do not belong in the nodes. **Avoid** `accept`/`visit` double dispatch when the classes are sealed and under your control: `when` with smart casts is enough. Keep the double-dispatch interface for types you cannot seal.

**Kotlin implementation** — `sealed interface Expr` has `Num`, `Add` and `Mul`. `fun Expr.eval()` and `fun Expr.show()` use `when (this)` with `is` branches, and no `else`. If you add `Sub`, both functions fail to compile until updated. That is the guarantee the classic pattern builds with `accept` methods. Smart casts make `left` and `right` available inside each branch. Gotcha: adding a new node type touches every operation, which is the trade-off of this pattern in both forms.

**Consequences** — New operations are cheap and checked by the compiler. New node types change every function.

**Related patterns** — **Composite** for the structure visited; **Iterator** supplies the traversal; **Strategy** for one algorithm chosen by the caller.

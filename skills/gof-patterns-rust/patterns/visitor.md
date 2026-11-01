# Visitor

An `enum` with free functions that `match` over it for closed hierarchies, or a `Visitor` trait with default walking methods when many visitors each care about a few nodes.

Refs: https://refactoring.guru/design-patterns/visitor/rust/example
Example: [examples/visitor.rs](../examples/visitor.rs)

**Intent** — Separate operations from the object structure they run over.

**Problem** — An expression tree needs evaluation, printing and later more operations, without bloating the node types.

**Applicability** — **Use** when the node set is stable but operations keep growing. **Avoid** accept-visit double dispatch when you control the enum: a free function with `match` over it is the visitor, and the compiler checks exhaustiveness for you.

**Rust implementation** — `enum Expr { Num, Add(Box<Expr>, Box<Expr>), Mul(..) }` with `fn eval(e: &Expr) -> f64` and `fn render(e: &Expr) -> String`, each a `match` over the enum. Adding a variant makes every `match` fail to compile, which is the intended trade. The `Visitor` trait is the second form: `visit` has a default body that walks the tree and calls `visit_num`, whose default does nothing, so `SumNums` overrides only `visit_num` and carries state in `&mut self`. Use it when there are many visitors that each handle a few node kinds, as `syn::visit::Visit` does.

**Consequences** — Operations added without touching nodes. The cost is that adding a node type changes every visitor.

**Related patterns** — **Composite** is the structure being visited; **Iterator** gives traversal without operations; **Command** for operations as values.

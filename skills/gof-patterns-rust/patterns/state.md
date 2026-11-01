# State

An `enum` of states with transition methods that take `self` by value and return the next state.

Refs: https://refactoring.guru/design-patterns/state/rust/example
Example: [examples/state.rs](../examples/state.rs)

**Intent** — Let an object act differently depending on its current state, with explicit transitions.

**Problem** — An order can be paid, shipped or cancelled only in certain states.

**Applicability** — **Use** when behaviour depends on a state that changes at runtime. **Avoid** State trait objects when the states are a closed set: an enum with `match` is enough. For compile-time states use typestate (`Order<Paid>`), which makes invalid transitions a compile error.

**Rust implementation** — `enum Order { Pending { items }, Paid { items, txn }, Shipped { tracking }, Cancelled }`. `fn pay(self, ..) -> Order` matches on `self`, moves data between variants, and returns the new state. Taking `self` by value prevents using the old state afterwards. The catch-all arm `other => other` returns the state unchanged and is the place to report an illegal transition. Use `Box<dyn State>` with `fn next(self: Box<Self>) -> Box<dyn State>` only when states are open for extension. The gotcha: transitioning through `&mut self` forces `mem::replace` or `take` tricks to move fields out.

**Consequences** — Exhaustive, checkable transitions. The cost is that adding a state touches every `match`.

**Related patterns** — **Strategy** has the same shape but the client swaps it, where state swaps itself; **Builder** shares the typestate technique; **Memento** for saving state to restore.

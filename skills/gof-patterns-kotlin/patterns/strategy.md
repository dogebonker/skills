# Strategy

A function type such as `(Double) -> Double` is the strategy interface, and lambdas or function references are the strategies.

Refs: https://refactoring.guru/design-patterns/strategy/java/example
Example: [examples/strategy.kt](../examples/strategy.kt)

**Intent** — Make a family of algorithms interchangeable behind one call shape.

**Problem** — Shipping cost depends on the delivery option, and branching on the option inside the cart grows with each new rule.

**Applicability** — **Use** when you have several ways to do one thing and want to choose or replace the way at runtime. **Avoid** a class per variant when each strategy is one function, which in Kotlin is nearly always: a lambda is enough. Keep an interface only when a strategy has several methods or needs state.

**Kotlin implementation** — `typealias ShippingCost = (weightKg: Double) -> Double` names the type, and `standard`, `express` and `pickup` are top-level lambdas. `Cart.choose` swaps one at runtime, and `choose { kg -> ... }` passes an ad hoc one. A `fun interface` gives a named single-method interface that still accepts lambda syntax, which helps Java callers. `Comparator`, `Executor` and `sortedBy { }` are strategies. Gotcha: lambdas capture variables, so avoid capturing mutable state or Activities in a strategy that outlives the screen.

**Consequences** — Few lines and easy testing. If strategies need names or state, you move back to classes.

**Related patterns** — **State** changes its behaviour by itself over time; **Command** for a request object, often with undo; **Template Method** varies steps by inheritance.

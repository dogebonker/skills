# State

An enum with associated values for the states and one `switch` on (state, event) that defines every transition.

Refs: https://refactoring.guru/design-patterns/state/swift/example
Example: [examples/state.swift](../examples/state.swift)

**Intent** — Let an object change its behavior when its internal state changes, as if it changed class.

**Problem** — An order behaves differently when pending, paid, shipped or cancelled, and `if` chains on flags multiply.

**Applicability** — **Use** when behavior depends on a state that changes at runtime and the transitions follow clear rules. **Avoid** a class per state when there are only a few states: an enum with a `switch` is enough, and the compiler checks exhaustiveness.

**Swift implementation** — Model `OrderState` as an enum whose cases carry data (`paid(receipt:)`) and a nested `Event` enum; `handling(_:)` returns the next state by switching on `(self, event)`, as the example does. Return `self` for ignored events or `throw` for illegal ones. Use the protocol-per-state version only when states have many methods or open extension. Avoid `default` hiding new cases when you want exhaustiveness.

**Consequences** — Transitions are visible in one place and impossible states are unrepresentable. A large machine makes one big switch.

**Related patterns** — **Strategy** swaps algorithms chosen by the client, State changes itself; **Command** for events; **Memento** keeps history.

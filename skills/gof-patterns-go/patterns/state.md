# State

A typed `iota` enum plus a transition table, or a state interface when each state has real behavior.

Refs: https://refactoring.guru/design-patterns/state/go/example
Example: [examples/state.go](../examples/state.go)

**Intent** — Let an object change its behavior as its internal state changes, with the valid transitions made explicit.

**Problem** — An order may only be shipped after payment and may be cancelled only before shipping.

**Applicability** — **Use** when there are several modes with rules about which transitions are legal. **Avoid** a type per state when two or three modes fit a bool or an enum: a `switch` is enough.

**Go implementation** — Define `type State int` with constants and a `String()` method, keep `transitions map[State][]State`, and implement `Order.To(next)` returning an `error` for illegal moves, as in the example. When states carry distinct behavior, define a `state` interface with methods like `Pay()` returning the next state, and keep the current one in a field. Gotcha: concurrent transitions need a mutex or compare-and-swap, because check-then-set is a race.

**Consequences** — Illegal transitions are caught in one place. The cost is a table to keep complete, or an interface type per state when behavior differs.

**Related patterns** — **Strategy** has similar structure but the client chooses the algorithm; **Command** for triggering transitions; **Memento** for saving and restoring states.

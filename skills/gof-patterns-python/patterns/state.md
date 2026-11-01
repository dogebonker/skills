# State

An object's behavior depends on its current state, modeled as an Enum and a transition table.

Refs: https://refactoring.guru/design-patterns/state/python/example
Example: [examples/state.py](../examples/state.py)

**Intent** — Let an object change what it does when its internal state changes, without sprawling conditionals.

**Problem** — An order can only ship after payment and cannot be cancelled once shipped; `if` chains on status flags multiply.

**Applicability** — **Use** when behavior depends on state and transitions follow rules. **Avoid** per-state classes when the differences are only which transitions are legal: an `Enum` plus a `dict[(state, event)] -> state` is clearer. Use state classes only when each state has substantial distinct behavior.

**Python implementation** — `OrderState` is an `Enum`; `TRANSITIONS` maps `(state, event)` to the next state. `Order.handle` looks up the pair and raises `ValueError` for illegal moves, re-raising with `from None` to hide the `KeyError`. For richer behavior, map each enum member to a handler function, or hold state objects that satisfy a Protocol. Gotcha: keep the table the only place transitions are defined, and test every illegal pair.

**Consequences** — Rules are data and easy to audit. Cost: behavior with many state-specific actions outgrows a table.

**Related patterns** — **Strategy** has the same shape but the client picks the algorithm, while states change themselves; **Flyweight** can share state objects; **Command** can be the event.

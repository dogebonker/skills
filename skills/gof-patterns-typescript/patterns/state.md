# State

A discriminated union describes each state's data, and one exhaustive `switch` on the tag defines which transitions are legal.

Refs: https://refactoring.guru/design-patterns/state/typescript/example
Example: [examples/state.ts](../examples/state.ts)

**Intent** — Change an object's behaviour when its internal state changes.

**Problem** — An order moves from pending to paid to shipped, and giant `if` chains over status flags let invalid combinations through.

**Applicability** — **Use** when behaviour and allowed actions depend on a state that changes at runtime. **Avoid** State subclasses when a union type with a `status` tag is enough: `never` makes the compiler enforce every case.

**TypeScript implementation** — `Order` is a union where each variant carries only its own data (`paid` has `paidAt`, `shipped` adds `tracking`). `transition(order, event)` switches on `order.status`, and `default` assigns to `never` so adding a state is a compile error until handled. Illegal moves throw. Classes with a `State` interface still fit when states hold complex behaviour. Gotcha: forget `break`/`return` and the fall-through is silent.

**Consequences** — Impossible states are unrepresentable and the compiler lists missing cases. The transition function can grow long for many states.

**Related patterns** — **Strategy** is chosen by the caller, not by internal transitions; **Visitor** uses the same union technique; **Memento** saves the state.

# State

Changes an object's behavior when its state changes; in JavaScript a transition table (object lookup) usually replaces a class per state.

Refs: https://github.com/HowProgrammingWorks/State  
Example: [examples/state.js](../examples/state.js)

**Intent** — Let an object alter its behavior when its internal state changes, so it appears to change its class.

**Problem** — Methods are full of `if (status === ...)` branches, and the rules about what is allowed in each state are scattered.

**Applicability** — **Use** for workflows with named states and guarded transitions (orders, connections, parsers). **Avoid** State subclasses when states differ only in which transitions are allowed: a lookup table is enough.

**JS implementation** — `TRANSITIONS` maps `state -> { action -> nextState }` as plain data, and `Shipment.dispatch` looks up the next state with `Object.hasOwn` and throws on an illegal action. Use a state object with methods (`{ enter, handle }`) only when each state carries real behavior; keep the lookup keyed by string names. Gotcha: `Object.freeze` is shallow, so the example freezes the table and every row.

**Consequences** — Rules are visible in one table and easy to test; behavior-heavy states need richer objects, and unknown actions must be handled explicitly.

**Related patterns** — **Strategy** for a caller-chosen algorithm rather than self-driven change; **Observer** announces transitions; **Memento** restores a previous state.

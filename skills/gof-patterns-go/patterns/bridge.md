# Bridge

A struct that holds an interface field, so the abstraction and the implementation vary separately.

Refs: https://refactoring.guru/design-patterns/bridge/go/example
Example: [examples/bridge.go](../examples/bridge.go)

**Intent** — Split a concept into an abstraction and an implementation hierarchy that can change independently.

**Problem** — Alerts and digests, each sent by email or Slack, would need four types, and every new channel doubles that.

**Applicability** — **Use** when you have two orthogonal axes (message kind and delivery channel) and want to combine them freely at runtime. **Avoid** a second interface hierarchy when only one axis varies or the combinations are few and fixed: a plain interface is enough.

**Go implementation** — Put the delivery behavior behind a small interface (`Sender`) and hold it in a field of each abstraction (`Alert`, `Digest`) as the example does. Pass the implementation in at construction. In Go this is just composition with an interface; no inheritance chain is involved. Keep the interface minimal (one method) so new implementations stay trivial. It looks like Strategy in code; the difference is intent, a whole abstraction family versus one swappable algorithm.

**Consequences** — Axes evolve independently and combine freely. The cost is an extra layer of indirection and an interface to keep stable.

**Related patterns** — **Strategy** has similar code but a single swappable algorithm; **Adapter** reconciles existing mismatched APIs; **Abstract Factory** for building the matching implementation.

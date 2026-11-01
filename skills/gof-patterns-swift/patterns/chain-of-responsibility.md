# Chain of Responsibility

An ordered list of handlers, each of which answers a request or passes it to the next.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/swift/example
Example: [examples/chain-of-responsibility.swift](../examples/chain-of-responsibility.swift)

**Intent** — Avoid coupling the sender to a specific receiver by giving several objects a chance to handle the request.

**Problem** — Support tickets, middleware, or validation steps need escalation, and the handler is not known in advance.

**Applicability** — **Use** when more than one object may handle a request, the set and order of handlers is configurable, or each step may stop processing. **Avoid** a linked chain of handler objects when one `if/else` or `switch` handles the cases: that, or an array of closures with `first(where:)`, is enough.

**Swift implementation** — Define `protocol SupportHandler { func handle(_:) -> String? }` and keep handlers in an array; the loop in `route` returns the first non-nil answer, as the example does. This avoids linked `next` references, which are harder to reorder and test. For middleware that wraps the next step, pass a `next` closure. Return an optional or a result enum to signal that nobody handled it.

**Consequences** — Flexible pipelines and loose coupling. A request can fall off the end unhandled, and flow is harder to trace.

**Related patterns** — **Decorator** wraps and always delegates; **Command** can supply the requests as objects; **Composite** can form the chain; **Mediator** routes between peers.

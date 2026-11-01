# Chain of Responsibility

A slice of handler functions tried in order until one reports it handled the request.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/go/example
Example: [examples/chain-of-responsibility.go](../examples/chain-of-responsibility.go)

**Intent** — Pass a request along a chain so several handlers get a chance to process it without the sender knowing which one will.

**Problem** — Expense approval depends on amount and validity, and the rules change often and in order.

**Applicability** — **Use** when several handlers may handle a request, the order matters, and the set of handlers changes at runtime or per configuration. **Avoid** a linked handler chain when exactly one handler is always known: a `switch` or ordered `if` list in one function is enough.

**Go implementation** — Define `type Handler func(Request) (handled bool, err error)` and iterate a slice, returning at the first handler that reports handled, as `run` does. Returning an `error` lets a handler reject instead of approve. Unlike HTTP middleware (see Decorator), each handler here decides whether to stop. For concurrency or cancellation, add a `context.Context` first parameter. Gotcha: a request no handler accepts must be reported, as the example's final error does.

**Consequences** — Handlers are decoupled and reorderable. The cost is that nothing guarantees a request gets handled, and tracing the path takes effort.

**Related patterns** — **Decorator** runs every layer, each wrapping the next; **Command** represents each request as an object; **Mediator** for components that must talk back and forth.

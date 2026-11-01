# Chain of Responsibility

A request passes along a list of handlers until one produces a result.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/python/example
Example: [examples/chain-of-responsibility.py](../examples/chain-of-responsibility.py)

**Intent** — Decouple the sender of a request from the objects that may handle it.

**Problem** — Authentication, rate limiting and routing each may reject or accept a request, and the set and order change by deployment.

**Applicability** — **Use** when several handlers might respond and the set should be configurable at runtime. **Avoid** the linked-handler class form where a `list` of callables and a loop do the job, as in `run_chain`.

**Python implementation** — A handler is `Callable[[Request], str | None]`, where `None` means pass to the next one. `run_chain` iterates the list and returns the first non-`None` result, with a default for unhandled requests. This puts order in data, so reordering is a list edit. Use `functools.reduce` or closures if each handler must call `next` (middleware style, wrapping the downstream call). Gotcha: decide explicitly what happens if nobody handles the request.

**Consequences** — Flexible order and loose coupling. Cost: no guarantee of handling, and a long chain is harder to debug.

**Related patterns** — **Command** objects can be the requests; **Decorator** has similar nesting but always forwards; **Composite** chains often follow a tree; **Mediator** routes among peers.

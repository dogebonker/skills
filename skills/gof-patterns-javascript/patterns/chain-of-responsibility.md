# Chain of Responsibility

Passes a request through a list of handlers, each of which answers or calls `next()`; in JavaScript this is an array of functions composed by a small runner.

Refs: https://github.com/HowProgrammingWorks/ChainOfResponsibility  
Example: [examples/chain-of-responsibility.js](../examples/chain-of-responsibility.js)

**Intent** — Decouple the sender of a request from the code that handles it by giving several handlers a chance to act in order.

**Problem** — Validation, authentication, throttling and routing all apply to one request, and the set or order changes per route.

**Applicability** — **Use** when handlers are optional, reorderable, or can stop the flow early. **Avoid** a chain when the sequence is fixed: calling the functions one after another is enough.

**JS implementation** — Handlers are `(req, next) => result` functions (`authenticate`, `rateLimit`); `chain(handlers, last)` builds the runner with a recursive `run(i)`. Returning without calling `next()` ends the chain. Keep state in closures: `rateLimit` holds its `hits` map and clears it when the fixed time window expires, so memory stays bounded. For async handlers, `await next()` and make the runner return promises. Gotcha: a forgotten `return` before `next()` silently drops the result.

**Consequences** — Handlers are small and reusable and the order is data; a request may fall off the end unhandled, and debugging needs logging of which handler stopped it.

**Related patterns** — **Decorator** for wrapping one function instead of routing through many; **Command** for turning the request itself into an object; **Mediator** for many-to-many coordination.

# Chain of Responsibility

Handlers share an interface and each holds an optional next handler to which it forwards requests it cannot answer.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/typescript/example
Example: [examples/chain-of-responsibility.ts](../examples/chain-of-responsibility.ts)

**Intent** — Pass a request along a chain until one handler deals with it.

**Problem** — An expense needs manager, director or CFO approval depending on the amount, and the sender should not know who decides.

**Applicability** — **Use** when several objects may handle a request, the handler is known only at runtime, or the order and set of handlers is configurable. **Avoid** linked handler objects when the set is fixed: a list of functions (`handlers.find((h) => h.canHandle(req))`) or a middleware array is enough.

**TypeScript implementation** — `LimitApprover` stores `#next` and returns `this.#next?.approve(req) ?? fallback`. `setNext` returns the next handler so chains are built fluently. Return a value from every path, including the end of chain. For middleware, `reduceRight` over an array of `(req, next) => res` functions yields the same behaviour. Gotcha: a request can fall off the end silently, so decide what happens then.

**Consequences** — Decouples sender from receivers and makes ordering configurable. Debugging is harder because the handler is not obvious, and a request may go unhandled.

**Related patterns** — **Decorator** always forwards; **Command** represents the request as an object; **Composite** chains often follow the parent links.

# Chain of Responsibility

Handlers are linked so each one either answers a request or passes it on, and a list of functions often does the same job.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/java/example
Example: [examples/chain-of-responsibility.kt](../examples/chain-of-responsibility.kt)

**Intent** — Pass a request along a chain of handlers until one deals with it.

**Problem** — A payment request must be checked for login, limit and more, and the set of checks changes by feature.

**Applicability** — **Use** when several objects may handle a request, the handler is not known in advance, and the order or set changes. **Avoid** a linked chain of handler classes when the steps are fixed and few: sequential calls in one function, or a `List<(Request) -> String?>` with `firstNotNullOfOrNull`, is enough.

**Kotlin implementation** — `Handler` holds an optional `next`. `AmountCheck`, `AuthCheck` and `LimitCheck` reject or call `super.handle(request)` to continue, and `Approve` ends the chain. Return a nullable result or a sealed result type to say whether anyone acted. The function-list version at the bottom of the example is shorter and easy to reorder. OkHttp interceptors and Android's touch event dispatch through views work as chains. Gotcha: a chain whose last handler is missing silently drops requests, so end it with a default handler.

**Consequences** — Handlers are decoupled and reorderable. Debugging a long chain is harder, and nothing guarantees handling.

**Related patterns** — **Command** can be the request passed along; **Decorator** wraps similarly, but every layer acts; **Composite** often supplies the tree a chain follows.

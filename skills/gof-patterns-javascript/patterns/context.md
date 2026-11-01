# Context

Exchanges state and dependencies between different components (abstractions, modules, layers) that do not share a common environment, without tightly coupling them.

Refs: https://github.com/HowProgrammingWorks/Context  
Example: [examples/context.js](../examples/context.js)

**Intent** — Pass capabilities (`console`, policy, `user`) as one bag or closure capture so services stay testable and environment-agnostic.

**Problem** — Global singletons or deep parameter lists for cross-cutting capabilities.

**Applicability** — **Use** per request/job in servers, CLI, or tests with fake context. **Avoid** a mutable mega-context that grows into a service locator: a small object with explicit fields is enough.

**JS implementation** — Object map injected into constructors (`AccountService`), or a factory that closes over destructured context fields (`createAccountService`). Gotcha: the closure style destructures once, so replacing `context.user` later does not reach a service that was already created.

**Consequences** — Replaces hidden singletons; document required keys; optional chaining does not replace explicit contracts in domain code.

**Related patterns** — **Singleton** for the hidden global that a context replaces, which lets tests pass a fake; **Strategy** often travels on the context as a field.

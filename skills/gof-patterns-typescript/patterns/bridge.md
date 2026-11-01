# Bridge

Two separate hierarchies, an abstraction and an implementation interface, joined by composition so each can vary alone.

Refs: https://refactoring.guru/design-patterns/bridge/typescript/example
Example: [examples/bridge.ts](../examples/bridge.ts)

**Intent** — Split a class that varies on two axes into two hierarchies connected by a reference.

**Problem** — Message types times delivery channels would need a subclass per combination (`SlackDeploy`, `PagerDeploy`, ...).

**Applicability** — **Use** when two independent dimensions of variation exist and combinations would otherwise multiply classes. **Avoid** a Bridge when only one axis varies: one class taking a `deliver: (text: string) => string` parameter is enough.

**TypeScript implementation** — `Channel` is the implementation interface; `slack` and `pager` are literals satisfying it. `Message` holds a `protected readonly channel` and subclasses (`DeploySucceeded`, `DatabaseDown`) call `deliver`. Parameter properties are avoided so the file also runs under Node's type stripping. Gotcha: with one axis only, Bridge is dead weight.

**Consequences** — Adds and swaps either axis independently and at runtime. It needs the split to be real, and is easy to apply too early.

**Related patterns** — **Strategy** has the same shape with a narrower purpose; **Adapter** fixes mismatches after the fact; **Abstract Factory** creates the matching implementation.

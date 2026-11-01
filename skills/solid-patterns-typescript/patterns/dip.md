# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf
Example: [examples/dip.ts](../examples/dip.ts)

**Principle** — Martin states two rules: high-level modules do not depend on low-level modules, and abstractions do not depend on details. The inversion is of ownership: the policy declares the interface and the detail conforms. In TypeScript the abstraction is a structural `interface` or function type, and injection is a constructor or function parameter, not a framework.

**Violation signals** — `new SmsGateway()`, `new PrismaClient()` or `fetch` inside a domain class (`OrderServiceV1`). Domain files importing from infrastructure folders. Tests that need module mocking (`jest.mock`) to replace a dependency.

**Fix** — `OrderService` declares `OrderNotifier` and takes it in the constructor. The composition root builds `smsNotifier` from the concrete `SmsGateway`. A test passes an object literal that records messages. No container is needed.

**When not to apply** — An interface with one implementation and no test double is ceremony; depend on the concrete class until a second implementation or a test needs the seam. Do not inject stable, pure dependencies (`Math`, `Intl`, your own pure helpers).

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) for an injected function; **Adapter** (`gof-patterns-typescript/patterns/adapter.md`) to fit a third-party client to the port; **Abstract Factory** (`gof-patterns-typescript/patterns/abstract-factory.md`) when the policy must create details; **Singleton** (`gof-patterns-typescript/patterns/singleton.md`), which injection replaces; **ISP** ([isp.md](isp.md)) keeps the port small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).

# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf
Example: [examples/dip.js](../examples/dip.js)

**Principle** — Martin states two rules: high-level modules do not depend on low-level modules, and abstractions do not depend on details. In JavaScript the abstraction is the shape of a parameter, often one function, and inversion means the policy receives the detail instead of calling `require` on it. Module-level imports of infrastructure are the usual hidden dependency.

**Violation signals** — Domain code that calls a module-level client (`placeOrderV1` calls `smsGateway.send`), `require('pg')` or `fetch` inside business rules, `new Date()` or `Math.random()` inside logic you need to test. Tests that rely on `jest.mock` or monkey-patching to swap a dependency.

**Fix** — `createOrderService({ notifyOrderConfirmed })` names the dependency it needs and returns the service. The composition root passes `smsGateway.send`; a test passes an arrow function that records messages. No container or interface declaration is needed.

**When not to apply** — Injecting every import is ceremony. Keep direct imports for pure helpers and stable standard APIs. Add the seam when a second implementation or a test actually needs it, and avoid a service locator that hides dependencies again.

**Related** — **Context** (`gof-patterns-javascript/patterns/context.md`) for passing capabilities per request; **Factory** (`gof-patterns-javascript/patterns/factory.md`) for `createX(deps)` functions; **Strategy** (`gof-patterns-javascript/patterns/strategy.md`) for an injected function; **Adapter** (`gof-patterns-javascript/patterns/adapter.md`) to fit a vendor client; **Singleton** (`gof-patterns-javascript/patterns/singleton.md`), which injection replaces; **ISP** ([isp.md](isp.md)); **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
